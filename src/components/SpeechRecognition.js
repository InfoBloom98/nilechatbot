import { useState, useEffect, useCallback } from 'react';

const SpeechRecognition = ({ onSpeechResult, onListening }) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [audioStream, setAudioStream] = useState(null);
  const [mediaRecorder, setMediaRecorder] = useState(null);
  const [audioChunks, setAudioChunks] = useState([]);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordingTimer, setRecordingTimer] = useState(null);

  useEffect(() => {
    // Check if the Web Speech API is available for direct transcription
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setIsSupported(true);
      console.log("Web Speech API is supported");
    } else if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      setIsSupported(true);
      console.log("MediaRecorder API is supported");
    } else {
      console.warn("Speech recognition is not supported in this browser");
    }
  }, []);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (recordingTimer) {
        clearInterval(recordingTimer);
      }
      if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
      }
    };
  }, [audioStream, recordingTimer]);

  // Define stopListening first (as a function declaration, not a callback yet)
  function stopListeningFn() {
    console.log("Stopping speech recognition...");
    
    // Clear the recording timer
    if (recordingTimer) {
      clearInterval(recordingTimer);
      setRecordingTimer(null);
    }
    
    // Stop Web Speech API if active
    if (window.speechRecognitionInstance) {
      try {
        window.speechRecognitionInstance.stop();
        window.speechRecognitionInstance = null;
      } catch (e) {
        console.log("Error stopping speech recognition:", e);
      }
    }
    
    // Stop MediaRecorder if active
    if (mediaRecorder && isListening) {
      try {
        // Check recorder state before stopping
        if (mediaRecorder.state !== 'inactive') {
          mediaRecorder.stop();
          console.log("Recorder stopped");
        }
        
        // Stop all tracks of the stream
        if (audioStream) {
          audioStream.getTracks().forEach(track => {
            track.stop();
            console.log("Audio track stopped");
          });
        }
      } catch (error) {
        console.error("Error stopping recorder:", error);
      }
      
      setIsListening(false);
      onListening && onListening(false);
    }
  }

  // Create memoized version after definition
  const stopListening = useCallback(stopListeningFn, [
    mediaRecorder, 
    isListening, 
    audioStream, 
    onListening, 
    recordingTimer
  ]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const startListening = useCallback(async () => {
    if (!isSupported) return;

    try {
      console.log("Starting speech recognition...");
      
      // Try to use Web Speech API if available
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        // Using native Web Speech API
        const recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        // Start recording duration counter
        setRecordingDuration(0);
        const timer = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
        }, 1000);
        setRecordingTimer(timer);
        
        recognition.onstart = () => {
          setIsListening(true);
          onListening && onListening(true);
        };
        
        recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          console.log("Transcript:", transcript);
          
          onSpeechResult && onSpeechResult({ 
            query: transcript 
          });
        };
        
        recognition.onerror = (event) => {
          console.error("Speech recognition error:", event.error);
          onSpeechResult && onSpeechResult({ 
            error: true, 
            message: `Error: ${event.error}` 
          });
        };
        
        recognition.onend = () => {
          setIsListening(false);
          onListening && onListening(false);
          clearInterval(timer);
          setRecordingTimer(null);
        };
        
        // Start recognition
        recognition.start();
        
        // Store reference to recognition for cleanup
        window.speechRecognitionInstance = recognition;
        
        // Auto-stop after 30 seconds
        setTimeout(() => {
          if (window.speechRecognitionInstance) {
            try {
              window.speechRecognitionInstance.stop();
            } catch (e) {
              console.log("Already stopped");
            }
          }
        }, 30000);
        
      } else {
        // Fallback to MediaRecorder approach
        // Request audio with higher quality settings
        const stream = await navigator.mediaDevices.getUserMedia({ 
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1,
            sampleRate: 44100
          } 
        });
        
        setAudioStream(stream);
        setIsListening(true);
        onListening && onListening(true);

        // Reset audio chunks and recording duration
        setAudioChunks([]);
        setRecordingDuration(0);

        // Set up timer to track recording duration
        const timer = setInterval(() => {
          setRecordingDuration(prev => prev + 1);
        }, 1000);
        setRecordingTimer(timer);

        // Create media recorder with specific MIME type
        const recorder = new MediaRecorder(stream, { 
          mimeType: 'audio/webm',
          audioBitsPerSecond: 128000
        });
        setMediaRecorder(recorder);

        // Set up event handlers
        recorder.ondataavailable = (event) => {
          console.log("Data available:", event.data.size);
          if (event.data.size > 0) {
            setAudioChunks(chunks => [...chunks, event.data]);
          }
        };

        recorder.onstop = async () => {
          console.log("Recorder stopped, processing audio...");
          clearInterval(recordingTimer);
          setRecordingTimer(null);
          
          // First check if we have any audio chunks
          if (audioChunks.length === 0) {
            console.error("No audio chunks recorded");
            onSpeechResult && onSpeechResult({ 
              error: true, 
              message: 'No audio recorded. Please try again.'
            });
            return;
          }

          try {
            // Create blob from chunks with specific type
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            console.log("Audio blob created:", audioBlob.size, "bytes");
            
            // Convert to base64
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            
            reader.onloadend = async () => {
              try {
                // Extract base64 data
                const base64data = reader.result.split(',')[1];
                console.log("Base64 data length:", base64data?.length || 0);
                
                if (!base64data) {
                  throw new Error("Failed to convert audio to base64");
                }
                
                // Check if we have enough audio data
                if (base64data.length < 100) {
                  throw new Error("Audio data too short, try speaking louder or longer");
                }
                
                // Send to backend for transcription only
                console.log("Sending to backend for transcription...");
                const response = await fetch('http://localhost:8000/api/transcribe', {
                  method: 'POST',
                  headers: {
                    'Content-Type': 'application/json',
                  },
                  body: JSON.stringify({
                    audio_data: base64data,
                    session_id: sessionStorage.getItem('sessionId') || 'default_session',
                  }),
                });

                if (!response.ok) {
                  const errorText = await response.text();
                  console.error("Backend error:", errorText);
                  throw new Error(`Server returned ${response.status}: ${errorText}`);
                }

                const data = await response.json();
                console.log("Received transcription:", data);
                
                // Return only the transcribed text for the input field
                onSpeechResult && onSpeechResult({
                  query: data.text
                });
              } catch (error) {
                console.error("Error processing audio:", error);
                onSpeechResult && onSpeechResult({ 
                  error: true, 
                  message: 'Failed to process speech: ' + error.message
                });
              }
            };
          } catch (error) {
            console.error("Error creating audio blob:", error);
            onSpeechResult && onSpeechResult({ 
              error: true, 
              message: 'Error processing audio data'
            });
          }
        };

        // Start recording with shorter timeslice for more frequent data
        recorder.start(500); // Get data every 500ms
        console.log("Recording started");
        
        // Auto-stop after 30 seconds as a safety measure
        setTimeout(() => {
          if (recorder.state === 'recording') {
            console.log("Auto-stopping after 30 seconds");
            stopListening(); // Use the memoized callback instead of the function directly
          }
        }, 30000);
      }
    } catch (error) {
      console.error("Microphone access error:", error);
      setIsSupported(false);
      onSpeechResult && onSpeechResult({ 
        error: true, 
        message: 'Could not access microphone: ' + error.message
      });
    }
  }, [isSupported, audioChunks, onListening, onSpeechResult, recordingTimer, stopListening]); // Added stopListening to deps

  return {
    isListening,
    isSupported,
    startListening,
    stopListening,
    recordingDuration
  };
};

export default SpeechRecognition; 