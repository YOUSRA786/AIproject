function searchSong() {
    const query = document.getElementById("songInput").value;
  
    fetch("/search", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
      const resultsDiv = document.getElementById("results");
      resultsDiv.innerHTML = "";
  
      data.forEach((track, index) => {
        const uri = track.uri;
        const trackHtml = `
          <div>
            <input type="checkbox" id="track-${index}" value="${uri}">
            <label for="track-${index}"><strong>${track.name}</strong> by ${track.artist}</label>
            <br>
            ${track.preview_url ? `<audio controls src="${track.preview_url}"></audio>` : 'No preview available'}
            <hr>
          </div>
        `;
        resultsDiv.innerHTML += trackHtml;
      });
    });
  }
  
  async function sendMessage() {
    const input = document.getElementById('user-input');
    const msg = input.value.trim();
    if (!msg) return;
  
    appendMessage('user', msg);
    input.value = '';
  
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
      });
  
      if (!res.ok) throw new Error("Server error");
  
      const data = await res.json();
      appendMessage('DJ', data.reply);
    } catch (err) {
      console.error(err);
      appendMessage('DJ', "⚠️ Error contacting the DJ assistant.");
    }
  }
  
  
  function createPlaylist() {
    const checkboxes = document.querySelectorAll("input[type='checkbox']:checked");
    const uris = Array.from(checkboxes).map(cb => cb.value);
  
    fetch("/create_playlist", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: "Yousra",
        tracks: uris
      })
    })
    .then(res => res.json())
    .then(data => {
      alert("Playlist created! 🎉 Click here: " + data.playlist_url);
      window.open(data.playlist_url, "_blank");
    })
    .catch(err => {
      console.error(err);
      alert("❌ Failed to create playlist.");
    });
  }
  