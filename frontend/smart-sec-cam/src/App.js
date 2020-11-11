import './App.css';
import ImageViewer from "./components/ImageViewer";

function App() {
  return (
    <div className="App">
      <ImageViewer room={"pi-sec-cam-1"} />
      <ImageViewer room={"scott-Aspire-E5-575"}/>
    </div>
  );
}

export default App;
