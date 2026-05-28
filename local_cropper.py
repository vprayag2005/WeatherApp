import os
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, HTTPServer
import json

# Minimal HTML for the cropper tool
HTML_CONTENT = """
<!DOCTYPE html>
<html>
<head>
    <title>Local District Map Cropper</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>
    <style>
        body { font-family: sans-serif; margin: 20px; display: flex; }
        #sidebar { width: 300px; padding-right: 20px; height: 90vh; overflow-y: auto; }
        #main { flex: 1; }
        .state-btn { display: block; width: 100%; padding: 8px; margin-bottom: 5px; text-align: left; cursor: pointer; }
        .state-btn.active { background: #007bff; color: white; border: none; }
        #image-container { max-height: 70vh; background: #eee; margin-top: 10px; }
        img { max-width: 100%; }
        pre { background: #222; color: #0f0; padding: 15px; border-radius: 5px; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h3>States</h3>
        <div id="state-list"></div>
    </div>
    <div id="main">
        <h2 id="title">Select a state</h2>
        <div id="image-container" style="display:none;">
            <img id="image" src="">
        </div>
        <div id="controls" style="display:none; margin-top: 20px;">
            <h3>Coordinates for DISTRICT_CROP_CONFIGS:</h3>
            <pre id="output">"State Name": (x, y, width, height),</pre>
            <p><i>Copy and paste the line above into services.py under DISTRICT_CROP_CONFIGS.</i></p>
        </div>
    </div>

    <script>
        const states = [
            "Andaman and Nicobar Islands", "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", 
            "Chandigarh", "Chhattisgarh", "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", 
            "Jammu and Kashmir", "Jharkhand", "Karnataka", "Kerala", "Ladakh", "Lakshadweep", 
            "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland", 
            "Odisha", "Puducherry", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", 
            "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ];
        
        let cropper = null;
        let currentState = null;
        
        const listDiv = document.getElementById("state-list");
        states.forEach(state => {
            const btn = document.createElement("button");
            btn.className = "state-btn";
            btn.innerText = state;
            btn.onclick = () => loadState(state, btn);
            listDiv.appendChild(btn);
        });
        
        function loadState(state, btnElement) {
            document.querySelectorAll(".state-btn").forEach(b => b.classList.remove("active"));
            btnElement.classList.add("active");
            
            currentState = state;
            document.getElementById("title").innerText = "Cropping: " + state;
            
            if (cropper) { cropper.destroy(); cropper = null; }
            
            const img = document.getElementById("image");
            // The image should be loaded from the local server
            // Ensure you have a raw uncropped image saved in your media folder, or just use the existing map image to test
            const stateSafe = state.replace(/ /g, "_");
            img.src = "/media/district_alert_images/district_alert_" + stateSafe + "_day_1.png";
            
            document.getElementById("image-container").style.display = "block";
            document.getElementById("controls").style.display = "block";
            
            img.onload = () => {
                cropper = new Cropper(img, {
                    viewMode: 1,
                    dragMode: 'crop',
                    autoCropArea: 0.8,
                    crop(event) {
                        const x = Math.round(event.detail.x);
                        const y = Math.round(event.detail.y);
                        const w = Math.round(event.detail.width);
                        const h = Math.round(event.detail.height);
                        document.getElementById("output").innerText = `"${currentState}": (${x}, ${y}, ${w}, ${h}),`;
                    }
                });
            };
            
            img.onerror = () => {
                document.getElementById("image-container").style.display = "none";
                document.getElementById("controls").style.display = "none";
                alert("Image not found! Make sure you have synced the state maps at least once.");
            };
        }
    </script>
</body>
</html>
"""

def run_server():
    # Save the HTML file
    with open("local_cropper.html", "w") as f:
        f.write(HTML_CONTENT)
        
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/' or self.path == '/index.html':
                self.path = '/local_cropper.html'
            return super().do_GET()
            
    port = 8080
    print(f"Starting local cropper tool at http://localhost:{port}")
    print("Press Ctrl+C to stop.")
    
    webbrowser.open(f"http://localhost:{port}")
    
    server = HTTPServer(('localhost', port), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        server.server_close()
        sys.exit(0)

if __name__ == "__main__":
    run_server()
