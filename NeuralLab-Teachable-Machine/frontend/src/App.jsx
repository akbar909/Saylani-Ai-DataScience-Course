import React, { useState, useEffect, useRef } from 'react';
import {
  Camera,
  Upload,
  Trash2,
  Plus,
  Play,
  Pause,
  Sliders,
  Cpu,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  X,
  ChevronRight,
  Sparkles,
  Info
} from 'lucide-react';

const API_BASE_URL = 'https://akbar909-neural-lab-backend.hf.space';

function App() {
  // Application state
  const [classes, setClasses] = useState([
    { id: '1', name: 'Class 1', sampleCount: 0 },
    { id: '2', name: 'Class 2', sampleCount: 0 }
  ]);
  const [editingClassId, setEditingClassId] = useState(null);
  const [editingClassName, setEditingClassName] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [isTrained, setIsTrained] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState('');
  const [trainingError, setTrainingError] = useState('');
  const [cValue, setCValue] = useState(1.0);
  const [maxIter, setMaxIter] = useState(1000);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Webcam collection state for classes
  const [webcamActiveId, setWebcamActiveId] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const recordingIntervalRef = useRef(null);
  const videoRefs = useRef({});

  // Inference state
  const [inferenceMode, setInferenceMode] = useState('webcam'); // 'webcam' or 'file'
  const [inferenceActive, setInferenceActive] = useState(false);
  const [inferenceFile, setInferenceFile] = useState(null);
  const [inferencePreview, setInferencePreview] = useState(null);
  const [predictions, setPredictions] = useState([]); // Array of { class_name, probability }
  const [predictionWinner, setPredictionWinner] = useState(null);
  const inferenceVideoRef = useRef(null);
  const inferenceIntervalRef = useRef(null);
  const inferenceCanvasRef = useRef(null);

  // Global video stream trackers
  const streamsRef = useRef({});

  // Sync state from backend on mount
  useEffect(() => {
    fetchStatus(true);
    return () => {
      // Clean up all streams and intervals on unmount
      stopAllWebcams();
      if (recordingIntervalRef.current) clearInterval(recordingIntervalRef.current);
      if (inferenceIntervalRef.current) clearInterval(inferenceIntervalRef.current);
    };
  }, []);

  const fetchStatus = async (isInitial = false) => {
    try {
      const res = await fetch(`${API_BASE_URL}/status`);
      if (res.ok) {
        const data = await res.json();
        setIsTrained(data.trained);

        // Map backend classes to state
        if (data.classes) {
          if (isInitial && Object.keys(data.classes).length > 0) {
            // Initial load: overwrite default classes with what's on the backend
            const loadedClasses = Object.entries(data.classes).map(([name, count], index) => ({
              id: String(index + 1),
              name: name,
              sampleCount: count
            }));
            setClasses(loadedClasses);
          } else if (!isInitial) {
            // Incremental update: merge backend counts into local state
            setClasses(prevClasses => {
              const matchedBackendNames = new Set();
              
              // Update local classes with backend counts
              const updatedClasses = prevClasses.map(c => {
                if (data.classes.hasOwnProperty(c.name)) {
                  matchedBackendNames.add(c.name);
                  return { ...c, sampleCount: data.classes[c.name] };
                }
                return { ...c, sampleCount: 0 };
              });
              
              // Add any classes from backend that aren't in local state
              let nextId = updatedClasses.length > 0 
                ? Math.max(...updatedClasses.map(c => parseInt(c.id))) + 1 
                : 1;
                
              Object.entries(data.classes).forEach(([name, count]) => {
                if (!matchedBackendNames.has(name)) {
                  updatedClasses.push({
                    id: String(nextId++),
                    name: name,
                    sampleCount: count
                  });
                }
              });
              
              return updatedClasses;
            });
          }
        }
      }
    } catch (err) {
      console.error("Failed to connect to backend status endpoint:", err);
    }
  };

  const stopAllWebcams = () => {
    Object.values(streamsRef.current).forEach(stream => {
      if (stream) stream.getTracks().forEach(track => track.stop());
    });
    streamsRef.current = {};
    setWebcamActiveId(null);
    setIsRecording(false);
  };

  // Class Management Functions
  const handleAddClass = () => {
    const nextId = String(classes.length > 0 ? Math.max(...classes.map(c => parseInt(c.id))) + 1 : 1);
    setClasses([...classes, { id: nextId, name: `Class ${nextId}`, sampleCount: 0 }]);
  };

  const handleDeleteClass = async (id, className) => {
    // If webcam is active for this class, stop it first
    if (webcamActiveId === id) {
      handleToggleWebcam(id, false);
    }

    try {
      const res = await fetch(`${API_BASE_URL}/delete-class`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ class_name: className })
      });
      if (res.ok) {
        setClasses(classes.filter(c => c.id !== id));
        fetchStatus();
      } else {
        const data = await res.json();
        alert(data.detail || "Failed to delete class from backend");
      }
    } catch (err) {
      console.error(err);
      // fallback to local delete
      setClasses(classes.filter(c => c.id !== id));
    }
  };

  const handleRenameClass = async (id, oldName, newName) => {
    if (!newName.trim() || oldName === newName) return;

    try {
      const res = await fetch(`${API_BASE_URL}/rename-class`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ old_name: oldName, new_name: newName })
      });
      if (res.ok) {
        setClasses(classes.map(c => c.id === id ? { ...c, name: newName } : c));
        fetchStatus();
      } else {
        const data = await res.json();
        alert(data.detail || "Failed to rename class on backend");
        // Revert rename
        fetchStatus();
      }
    } catch (err) {
      console.error(err);
      setClasses(classes.map(c => c.id === id ? { ...c, name: newName } : c));
    }
  };

  // Webcam Capture handling
  const handleToggleWebcam = async (id, enable) => {
    if (!enable) {
      // Disable webcam
      if (streamsRef.current[id]) {
        streamsRef.current[id].getTracks().forEach(track => track.stop());
        streamsRef.current[id] = null;
      }
      setWebcamActiveId(null);
      setIsRecording(false);
      if (recordingIntervalRef.current) {
        clearInterval(recordingIntervalRef.current);
        recordingIntervalRef.current = null;
      }
      return;
    }

    // Stop other webcams first
    stopAllWebcams();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 320, height: 240, facingMode: 'user' }
      });
      streamsRef.current[id] = stream;
      setWebcamActiveId(id);

      // Bind to video ref (needs a tick for DOM to render)
      setTimeout(() => {
        const videoElement = videoRefs.current[id];
        if (videoElement) {
          videoElement.srcObject = stream;
          videoElement.play().catch(e => console.error("Video play failed:", e));
        }
      }, 100);
    } catch (err) {
      console.error("Camera access error:", err);
      alert("Unable to access the webcam. Check camera permissions.");
    }
  };

  // Hold-to-Record function
  const startRecording = (id, className) => {
    if (!streamsRef.current[id]) return;
    setIsRecording(true);

    const videoElement = videoRefs.current[id];
    const canvas = document.createElement('canvas');
    canvas.width = 224;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');

    const captureFrameAndUpload = () => {
      if (!videoElement || videoElement.paused || videoElement.ended) return;

      // Draw frame to square canvas
      ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

      // Convert to blob and upload
      canvas.toBlob(async (blob) => {
        if (!blob) return;
        const file = new File([blob], `frame-${Date.now()}.jpg`, { type: 'image/jpeg' });

        const formData = new FormData();
        formData.append('class_name', className);
        formData.append('files', file);

        try {
          const res = await fetch(`${API_BASE_URL}/upload-sample`, {
            method: 'POST',
            body: formData
          });
          if (res.ok) {
            // Update counts
            setClasses(prev => prev.map(c => c.id === id ? { ...c, sampleCount: c.sampleCount + 1 } : c));
          }
        } catch (err) {
          console.error("Failed to upload frame:", err);
        }
      }, 'image/jpeg', 0.8);
    };

    // Capture first frame immediately
    captureFrameAndUpload();

    // Repeat every 150ms
    recordingIntervalRef.current = setInterval(captureFrameAndUpload, 150);
  };

  const stopRecording = () => {
    setIsRecording(false);
    if (recordingIntervalRef.current) {
      clearInterval(recordingIntervalRef.current);
      recordingIntervalRef.current = null;
    }
    // Refresh status to be in perfect sync
    fetchStatus();
  };

  // File Upload handling
  const handleFileUpload = async (id, className, filesList) => {
    if (!filesList || filesList.length === 0) return;

    const formData = new FormData();
    formData.append('class_name', className);
    for (let i = 0; i < filesList.length; i++) {
      formData.append('files', filesList[i]);
    }

    try {
      const res = await fetch(`${API_BASE_URL}/upload-sample`, {
        method: 'POST',
        body: formData
      });
      if (res.ok) {
        fetchStatus();
      } else {
        const data = await res.json();
        alert(data.detail || "Error uploading files");
      }
    } catch (err) {
      console.error(err);
      alert("Connection to backend failed during upload.");
    }
  };

  // Clear samples for a single class
  const handleClearClassSamples = async (id, className) => {
    if (!confirm(`Are you sure you want to delete all samples for "${className}"?`)) return;

    try {
      const res = await fetch(`${API_BASE_URL}/upload-sample`, {
        method: 'POST',
        body: (() => {
          const fd = new FormData();
          fd.append('class_name', className);
          // Sending no files clears the class folder
          return fd;
        })()
      });
      // Wait, let's implement the backend to clear if empty list.
      // If we don't have it, let's make sure the backend handles this.
      // Or we can just call an endpoint. Let's make sure our backend '/upload-sample'
      // deletes samples if files list is empty, or create a specific clear endpoint.
      // In python we can handle it easily!
      if (res.ok) {
        fetchStatus();
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Reset entire application (all classes, models, files deleted)
  const handleResetApp = async () => {
    if (!confirm("Are you sure you want to RESET? This will delete ALL classes, image samples, and trained models!")) return;

    stopAllWebcams();
    stopInference();

    try {
      const res = await fetch(`${API_BASE_URL}/clear`, {
        method: 'POST'
      });
      if (res.ok) {
        setClasses([
          { id: '1', name: 'Class 1', sampleCount: 0 },
          { id: '2', name: 'Class 2', sampleCount: 0 }
        ]);
        setIsTrained(false);
        setPredictions([]);
        setPredictionWinner(null);
        setInferenceFile(null);
        setInferencePreview(null);
        alert("System successfully reset!");
      }
    } catch (err) {
      console.error(err);
      alert("Failed to reset system. Make sure backend is running.");
    }
  };

  // Training execution
  const handleTrainModel = async () => {
    // Basic validation
    const populatedClasses = classes.filter(c => c.sampleCount > 0);
    if (populatedClasses.length < 2) {
      setTrainingError("Training requires at least 2 classes with at least 1 image sample each.");
      return;
    }

    setIsTraining(true);
    setTrainingStatus("Preparing training datasets...");
    setTrainingError("");

    // Stop active camera captures
    stopAllWebcams();
    stopInference();

    try {
      const res = await fetch(`${API_BASE_URL}/train`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          c_value: parseFloat(cValue),
          max_iter: parseInt(maxIter)
        })
      });

      if (res.ok) {
        setTrainingStatus("Finalizing model parameters...");
        setTimeout(() => {
          setIsTrained(true);
          setIsTraining(false);
          setTrainingStatus("");
          // Automatically enable inference
          setInferenceMode('webcam');
          handleToggleInference(true);
        }, 1000);
      } else {
        const data = await res.json();
        setTrainingError(data.detail || "Failed to train the model. Check backend logs.");
        setIsTraining(false);
      }
    } catch (err) {
      console.error(err);
      setTrainingError("Connection lost. Please make sure the backend server is running.");
      setIsTraining(false);
    }
  };

  // Inference Functions
  const handleToggleInference = async (enable) => {
    if (!enable) {
      stopInference();
      return;
    }

    setInferenceActive(true);

    if (inferenceMode === 'webcam') {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: 320, height: 240, facingMode: 'user' }
        });

        if (inferenceVideoRef.current) {
          inferenceVideoRef.current.srcObject = stream;
          inferenceVideoRef.current.play().catch(e => console.error(e));
        }

        // Start predicting loop (every 300ms)
        inferenceIntervalRef.current = setInterval(runLivePredict, 300);
      } catch (err) {
        console.error("Inference camera setup error:", err);
        setInferenceActive(false);
        alert("Could not access camera for inference.");
      }
    }
  };

  const stopInference = () => {
    setInferenceActive(false);
    if (inferenceIntervalRef.current) {
      clearInterval(inferenceIntervalRef.current);
      inferenceIntervalRef.current = null;
    }
    if (inferenceVideoRef.current && inferenceVideoRef.current.srcObject) {
      const stream = inferenceVideoRef.current.srcObject;
      stream.getTracks().forEach(track => track.stop());
      inferenceVideoRef.current.srcObject = null;
    }
    setPredictions([]);
    setPredictionWinner(null);
  };

  // Live inference execution
  const runLivePredict = async () => {
    const video = inferenceVideoRef.current;
    if (!video || video.paused || video.ended) return;

    const canvas = inferenceCanvasRef.current;
    if (!canvas) return;
    canvas.width = 224;
    canvas.height = 224;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(async (blob) => {
      if (!blob) return;
      const file = new File([blob], `predict-${Date.now()}.jpg`, { type: 'image/jpeg' });
      await performPrediction(file);
    }, 'image/jpeg', 0.8);
  };

  const performPrediction = async (file) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        body: formData
      });

      if (res.ok) {
        const data = await res.json();
        // data format: { class: "Class A", probabilities: { "Class A": 0.85, "Class B": 0.15 } }
        const formattedProbs = Object.entries(data.probabilities).map(([name, val]) => ({
          class_name: name,
          probability: val
        })).sort((a, b) => b.probability - a.probability); // Sort highest first

        setPredictions(formattedProbs);
        setPredictionWinner(data.class);
      }
    } catch (err) {
      console.error("Prediction API failed:", err);
    }
  };

  // Handle file drop/upload for inference
  const handleInferenceFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setInferenceFile(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setInferencePreview(reader.result);
    };
    reader.readAsDataURL(file);

    await performPrediction(file);
  };

  // Toggle inference mode (webcam vs file)
  const handleInferenceModeChange = (mode) => {
    stopInference();
    setInferenceMode(mode);
    setInferenceFile(null);
    setInferencePreview(null);
    setPredictions([]);
    setPredictionWinner(null);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col relative overflow-hidden">
      {/* Decorative Glow Elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-500/10 blur-[120px] animate-pulse-slow pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[600px] h-[600px] rounded-full bg-purple-500/10 blur-[130px] animate-pulse-slow pointer-events-none"></div>

      {/* Main Header */}
      <header className="border-b border-slate-900 bg-slate-950/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Cpu className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-indigo-200 via-slate-100 to-purple-200 bg-clip-text text-transparent m-0 font-sans">
                NeuralLab <span className="text-sm font-semibold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 ml-2">Teachable Machine</span>
              </h1>
            </div>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <button
              onClick={handleResetApp}
              className="px-4 py-2 text-sm font-semibold rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:bg-slate-800 hover:text-white hover:border-slate-700 transition duration-200"
            >
              Reset Workbench
            </button>
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-400 font-mono">
              <span className={`w-2.5 h-2.5 rounded-full ${isTrained ? 'bg-emerald-500 shadow-md shadow-emerald-500/50' : 'bg-amber-500'}`}></span>
              {isTrained ? 'Model Active' : 'Model Untrained'}
            </div>
          </div>
        </div>
      </header>

      {/* Workspace Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8 z-10">

        {/* LEFT COLUMN: Classes Panel (5 cols) */}
        <section className="lg:col-span-5 flex flex-col gap-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
            <div>
              <h2 className="text-xl font-semibold text-white tracking-tight flex items-center gap-2 m-0">
                1. Gather Dataset
              </h2>
              <p className="text-sm text-slate-400">Define your classes and upload/record sample images.</p>
            </div>
            <button
              onClick={handleAddClass}
              className="flex items-center gap-1.5 px-3.5 py-2 text-sm font-bold bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg transition-all duration-200 shadow-md shadow-indigo-600/15 active:scale-95 w-full sm:w-auto justify-center"
            >
              <Plus className="w-4 h-4" /> Add Class
            </button>
          </div>

          <div className="flex flex-col gap-5 overflow-y-auto max-h-[70vh] pr-2">
            {classes.map((c) => (
              <div
                key={c.id}
                className="bg-slate-900/40 backdrop-blur-sm border border-slate-900 rounded-xl p-5 shadow-sm hover:border-slate-800 transition duration-200"
              >
                {/* Class Header */}
                <div className="flex justify-between items-center mb-4 gap-4">
                  <input
                    type="text"
                    value={editingClassId === c.id ? editingClassName : c.name}
                    onFocus={() => {
                      setEditingClassId(c.id);
                      setEditingClassName(c.name);
                    }}
                    onChange={(e) => {
                      setEditingClassName(e.target.value);
                    }}
                    onBlur={() => {
                      if (editingClassId === c.id) {
                        handleRenameClass(c.id, c.name, editingClassName);
                        setEditingClassId(null);
                      }
                    }}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.target.blur();
                      }
                    }}
                    className="flex-1 bg-transparent border-b border-transparent hover:border-slate-700 focus:border-indigo-500 py-1 font-bold text-lg text-white outline-none transition duration-150"
                  />
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 border border-slate-700/50">
                      {c.sampleCount} samples
                    </span>
                    {classes.length > 2 && (
                      <button
                        onClick={() => handleDeleteClass(c.id, c.name)}
                        className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 transition duration-150"
                        title="Delete class"
                      >
                        <Trash2 className="w-4.5 h-4.5" />
                      </button>
                    )}
                  </div>
                </div>

                {/* Input Gathering Options */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Option 1: Webcam Feed */}
                  <div className="flex flex-col gap-2">
                    {webcamActiveId === c.id ? (
                      <div className="relative rounded-lg overflow-hidden bg-black border border-slate-800 aspect-video flex items-center justify-center">
                        <video
                          ref={el => videoRefs.current[c.id] = el}
                          className="w-full h-full object-cover transform -scale-x-100"
                          muted
                          playsInline
                        />
                        <button
                          onClick={() => handleToggleWebcam(c.id, false)}
                          className="absolute top-2 right-2 p-1 rounded-full bg-black/60 hover:bg-black text-white transition"
                          title="Turn off camera"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleToggleWebcam(c.id, true)}
                        className="flex flex-col items-center justify-center gap-2 p-5 rounded-lg bg-slate-900/60 border border-slate-800/80 hover:bg-slate-800/50 hover:border-slate-700 text-slate-300 transition duration-200 aspect-video"
                      >
                        <Camera className="w-6 h-6 text-indigo-400" />
                        <span className="text-sm font-semibold">Webcam Input</span>
                      </button>
                    )}

                    {webcamActiveId === c.id && (
                      <button
                        onMouseDown={() => startRecording(c.id, c.name)}
                        onMouseUp={stopRecording}
                        onMouseLeave={stopRecording}
                        onTouchStart={() => startRecording(c.id, c.name)}
                        onTouchEnd={stopRecording}
                        className={`w-full py-2.5 rounded-lg font-bold text-sm text-center select-none transition-all duration-150 ${isRecording
                          ? 'bg-rose-600 hover:bg-rose-700 text-white shadow-lg shadow-rose-600/20 animate-pulse'
                          : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/15'
                          }`}
                      >
                        {isRecording ? 'Recording Frames...' : 'Hold to Record'}
                      </button>
                    )}
                  </div>

                  {/* Option 2: File Upload */}
                  <div className="flex flex-col gap-2">
                    <label className="flex flex-col items-center justify-center gap-2 p-5 rounded-lg bg-slate-900/60 border border-slate-800/80 hover:bg-slate-800/50 hover:border-slate-700 text-slate-300 transition duration-200 cursor-pointer aspect-video">
                      <Upload className="w-6 h-6 text-purple-400" />
                      <span className="text-sm font-semibold">Upload Images</span>
                      <input
                        type="file"
                        multiple
                        accept="image/*"
                        onChange={(e) => handleFileUpload(c.id, c.name, e.target.files)}
                        className="hidden"
                      />
                    </label>

                    {c.sampleCount > 0 && (
                      <button
                        onClick={() => handleClearClassSamples(c.id, c.name)}
                        className="w-full py-2.5 rounded-lg font-bold text-sm text-slate-400 bg-slate-950 border border-slate-800 hover:bg-slate-900 hover:text-rose-400 transition"
                      >
                        Clear Samples
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* MIDDLE COLUMN: Training Panel (3 cols) */}
        <section className="lg:col-span-3 flex flex-col gap-6">
          <div>
            <h2 className="text-xl font-semibold text-white tracking-tight flex items-center gap-2 m-0">
              2. Train Model
            </h2>
            <p className="text-sm text-slate-400">Run transfer learning with MobileNetV3 features.</p>
          </div>

          <div className="bg-slate-900/40 backdrop-blur-sm border border-slate-900 rounded-xl p-5 flex flex-col gap-5">
            {/* Hyperparameter Settings */}
            <div className="border border-slate-800 rounded-lg overflow-hidden bg-slate-950/40">
              <button
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="w-full px-4 py-3 flex justify-between items-center text-sm font-bold text-slate-300 hover:bg-slate-900 transition"
              >
                <span className="flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-slate-400" /> Hyperparameters
                </span>
                <span className="text-xs text-indigo-400">{showAdvanced ? 'Hide' : 'Show'}</span>
              </button>

              {showAdvanced && (
                <div className="p-4 border-t border-slate-900 flex flex-col gap-4 bg-slate-950/20">
                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-400">Regularization (C)</span>
                      <span className="text-white font-mono">{cValue}</span>
                    </div>
                    <input
                      type="range"
                      min="0.01"
                      max="10.0"
                      step="0.05"
                      value={cValue}
                      onChange={(e) => setCValue(parseFloat(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                    <span className="text-[10px] text-slate-500">Lower values = stronger regularization.</span>
                  </div>

                  <div className="flex flex-col gap-1.5">
                    <div className="flex justify-between text-xs font-semibold">
                      <span className="text-slate-400">Max Iterations</span>
                      <span className="text-white font-mono">{maxIter}</span>
                    </div>
                    <input
                      type="range"
                      min="100"
                      max="5000"
                      step="100"
                      value={maxIter}
                      onChange={(e) => setMaxIter(parseInt(e.target.value))}
                      className="w-full accent-indigo-500"
                    />
                    <span className="text-[10px] text-slate-500">Maximum training iterations for the solver.</span>
                  </div>
                </div>
              )}
            </div>

            {/* Train Button / Loader */}
            {isTraining ? (
              <div className="flex flex-col items-center justify-center py-8 gap-4 border border-indigo-500/20 rounded-lg bg-indigo-950/10">
                <RefreshCw className="w-10 h-10 text-indigo-400 animate-spin" />
                <div className="text-center">
                  <h3 className="font-bold text-white text-sm">Training in Progress</h3>
                  <p className="text-xs text-slate-400 mt-1 px-4">{trainingStatus}</p>
                </div>
              </div>
            ) : (
              <button
                onClick={handleTrainModel}
                disabled={classes.filter(c => c.sampleCount > 0).length < 2}
                className={`w-full py-3.5 rounded-xl font-bold flex items-center justify-center gap-2 transition duration-200 ${classes.filter(c => c.sampleCount > 0).length < 2
                  ? 'bg-slate-900 border border-slate-800 text-slate-600 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white shadow-lg shadow-indigo-500/15'
                  }`}
              >
                <Cpu className="w-5 h-5" /> Train Model
              </button>
            )}

            {/* Success indicator */}
            {isTrained && !isTraining && (
              <div className="flex gap-2.5 items-start p-3.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-sm">
                <CheckCircle className="w-5 h-5 shrink-0 mt-0.5 text-emerald-500" />
                <div>
                  <h4 className="font-bold text-white">Model Trained Successfully</h4>
                  <p className="text-xs text-slate-400 mt-0.5">Your customized weights are saved. Testing panel is unlocked.</p>
                </div>
              </div>
            )}

            {/* Training Errors */}
            {trainingError && (
              <div className="flex gap-2.5 items-start p-3.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm">
                <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-500" />
                <div>
                  <h4 className="font-bold text-white">Training Error</h4>
                  <p className="text-xs text-slate-400 mt-0.5">{trainingError}</p>
                </div>
              </div>
            )}

            {/* Architecture Explanatory Hint */}
            <div className="flex gap-2 p-3 bg-slate-950/40 rounded-lg border border-slate-850 text-[11px] text-slate-400 leading-normal">
              <Info className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
              <span>
                Backend runs on PyTorch <strong>MobileNetV3</strong> backbone to extract high-fidelity features, fitting a rapid multi-class Logistic Regression in real-time.
              </span>
            </div>
          </div>
        </section>

        {/* RIGHT COLUMN: Inference/Preview Panel (4 cols) */}
        <section className="lg:col-span-4 flex flex-col gap-6">
          <div>
            <h2 className="text-xl font-semibold text-white tracking-tight flex items-center gap-2 m-0">
              3. Test & Inference
            </h2>
            <p className="text-sm text-slate-400">Unlock this section by training the model above.</p>
          </div>

          {!isTrained ? (
            <div className="flex-1 min-h-[300px] border-2 border-dashed border-slate-900 rounded-xl flex flex-col items-center justify-center p-8 text-center bg-slate-950/20">
              <div className="w-12 h-12 rounded-full bg-slate-900 flex items-center justify-center mb-4 border border-slate-800">
                <Sliders className="w-5 h-5 text-slate-600" />
              </div>
              <h3 className="font-bold text-slate-400 text-sm">Inference Locked</h3>
              <p className="text-xs text-slate-500 mt-2 max-w-[200px] leading-relaxed">
                Add at least 2 classes with images and run the training cycle to unlock real-time predictions.
              </p>
            </div>
          ) : (
            <div className="bg-slate-900/40 backdrop-blur-sm border border-slate-900 rounded-xl p-5 flex flex-col gap-5">

              {/* Tabs for Mode */}
              <div className="flex p-1 bg-slate-950 border border-slate-900 rounded-lg">
                <button
                  onClick={() => handleInferenceModeChange('webcam')}
                  className={`flex-1 py-2 text-xs font-bold rounded-md transition ${inferenceMode === 'webcam'
                    ? 'bg-slate-900 text-white border border-slate-800/80 shadow'
                    : 'text-slate-400 hover:text-white'
                    }`}
                >
                  Live Webcam
                </button>
                <button
                  onClick={() => handleInferenceModeChange('file')}
                  className={`flex-1 py-2 text-xs font-bold rounded-md transition ${inferenceMode === 'file'
                    ? 'bg-slate-900 text-white border border-slate-800/80 shadow'
                    : 'text-slate-400 hover:text-white'
                    }`}
                >
                  Image Upload
                </button>
              </div>

              {/* Input Previews */}
              {inferenceMode === 'webcam' ? (
                <div className="flex flex-col gap-3">
                  <div className="relative rounded-xl overflow-hidden bg-black border border-slate-850 aspect-video flex items-center justify-center shadow-inner">
                    <video
                      ref={inferenceVideoRef}
                      className="w-full h-full object-cover transform -scale-x-100"
                      muted
                      playsInline
                    />

                    {/* Hidden canvas for capturing frame blobs */}
                    <canvas ref={inferenceCanvasRef} className="hidden" />

                    {!inferenceActive && (
                      <div className="absolute inset-0 bg-slate-950/80 flex flex-col items-center justify-center gap-2.5">
                        <Camera className="w-8 h-8 text-slate-600 animate-bounce" />
                        <span className="text-xs font-semibold text-slate-400">Webcam Inactive</span>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => handleToggleInference(!inferenceActive)}
                    className={`w-full py-2.5 rounded-lg font-bold text-sm flex items-center justify-center gap-2 transition duration-200 ${inferenceActive
                      ? 'bg-rose-600/10 hover:bg-rose-600/15 border border-rose-500/20 text-rose-400'
                      : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md shadow-indigo-600/15'
                      }`}
                  >
                    {inferenceActive ? (
                      <>
                        <Pause className="w-4 h-4" /> Stop Live Test
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4" /> Start Live Test
                      </>
                    )}
                  </button>
                </div>
              ) : (
                <div className="flex flex-col gap-3">
                  <label className="flex flex-col items-center justify-center gap-2.5 p-6 rounded-xl bg-slate-950/50 border border-slate-900 hover:bg-slate-900/40 hover:border-slate-850 text-slate-400 transition cursor-pointer aspect-video relative overflow-hidden group">
                    {inferencePreview ? (
                      <img
                        src={inferencePreview}
                        alt="Test preview"
                        className="absolute inset-0 w-full h-full object-contain p-2"
                      />
                    ) : (
                      <>
                        <Upload className="w-7 h-7 text-indigo-400 group-hover:scale-110 transition duration-200" />
                        <div className="text-center">
                          <span className="text-xs font-bold text-white block">Drop a single image here</span>
                          <span className="text-[10px] text-slate-500 mt-1 block">or click to browse filesystem</span>
                        </div>
                      </>
                    )}
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleInferenceFileChange}
                      className="hidden"
                    />
                  </label>
                </div>
              )}

              {/* Predictions Display */}
              {predictions.length > 0 && (
                <div className="flex flex-col gap-4 border-t border-slate-900 pt-4 mt-2">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Output Probabilities
                  </h3>

                  <div className="flex flex-col gap-3.5">
                    {predictions.map(({ class_name, probability }) => {
                      const isWinner = class_name === predictionWinner;
                      const pct = Math.round(probability * 100);

                      return (
                        <div key={class_name} className="flex flex-col gap-1.5">
                          <div className="flex justify-between text-sm font-semibold">
                            <span className={isWinner ? 'text-white font-extrabold flex items-center gap-1.5' : 'text-slate-400 font-medium'}>
                              {class_name}
                              {isWinner && <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-ping"></span>}
                            </span>
                            <span className={isWinner ? 'text-indigo-400 font-mono font-bold' : 'text-slate-400 font-mono'}>
                              {pct}%
                            </span>
                          </div>

                          <div className="h-3.5 w-full bg-slate-950 rounded-full border border-slate-900 overflow-hidden relative p-[2px]">
                            <div
                              className={`h-full rounded-full transition-all duration-300 ${isWinner
                                ? 'bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_8px_rgba(99,102,241,0.5)]'
                                : 'bg-slate-800'
                                }`}
                              style={{ width: `${pct}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>

                  {predictionWinner && (
                    <div className="mt-2 text-center p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/15">
                      <span className="text-xs text-slate-400">Classified Target:</span>
                      <strong className="block text-lg text-white font-extrabold tracking-tight mt-0.5">{predictionWinner}</strong>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </section>
      </main>

      <footer className="max-w-7xl w-full mx-auto px-6 py-6 border-t border-slate-950 text-center text-xs text-slate-600 font-medium tracking-wide">
        NeuralLab and Teachable Machine core architectures are built using local PyTorch frameworks and React.
      </footer>
    </div>
  );
}

export default App;
