let input = document.getElementById("question");

input.addEventListener("keypress", function(event){
    if(event.key === "Enter"){
        askAI();
    }
});

function stopSpeech(){
    window.speechSynthesis.cancel();
   
}
window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
};

function cleanText(text){
    return text
        .replace(/\*/g, "")
        .replace(/_/g, "")
        .replace(/#/g, "")
        .replace(/`/g, "")
        .replace(/\n/g, " ")
        .replace(/\s+/g, " ")
        .trim();
}

function speakText(text){
    stopSpeech();

    let speech = new SpeechSynthesisUtterance();
    speech.text = cleanText(text);
    speech.rate = 0.95;
    speech.pitch = 1;
    speech.volume = 1;

    let voices = window.speechSynthesis.getVoices();

    let selectedVoice =
        voices.find(v => v.name.includes("Google UK English Female")) ||
        voices.find(v => v.name.includes("Google US English")) ||
        voices.find(v => v.lang === "en-IN") ||
        voices[0];

    if(selectedVoice){
        speech.voice = selectedVoice;
    }

    window.speechSynthesis.speak(speech);
}

async function askAI(){

    let question = input.value;

    if(question.trim() === "") return;

    let chatBox = document.getElementById("chatBox");

    let userMsg = document.createElement("div");
    userMsg.className = "message user";
    userMsg.innerText = question;
    chatBox.appendChild(userMsg);

    input.value = "";

    let thinking = document.createElement("div");
    thinking.className = "message ai thinking";
    thinking.innerText = "AI is thinking...";
    chatBox.appendChild(thinking);

    chatBox.scrollTop = chatBox.scrollHeight;

    try {
        let response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({question: question})
        });

        let data = await response.json();

        thinking.remove();

        let aiWrapper = document.createElement("div");
        aiWrapper.className = "ai-wrapper";

        let aiMsg = document.createElement("div");
        aiMsg.className = "message ai";

        if(data.answer){
            aiMsg.innerText = data.answer;
        } else if(data.error){
            aiMsg.innerText = "Error: " + data.error;
        } else {
            aiMsg.innerText = "No response received.";
        }

        let controls = document.createElement("div");
        controls.className = "voice-controls";

        let playBtn = document.createElement("button");
        playBtn.className = "voice-btn";
        playBtn.innerText = "🔊 Play";
        playBtn.onclick = function(){
            speakText(aiMsg.innerText);
        };

        let stopBtn = document.createElement("button");
        stopBtn.className = "voice-btn stop-btn";
        stopBtn.innerText = "⏹ Stop";
        stopBtn.onclick = function(){
            stopSpeech();
        };

        controls.appendChild(playBtn);
        controls.appendChild(stopBtn);

        aiWrapper.appendChild(aiMsg);
        aiWrapper.appendChild(controls);

        chatBox.appendChild(aiWrapper);
        chatBox.scrollTop = chatBox.scrollHeight;

    } catch(error){
        thinking.remove();

        let errorMsg = document.createElement("div");
        errorMsg.className = "message ai";
        errorMsg.innerText = "Something went wrong while connecting to AI.";
        chatBox.appendChild(errorMsg);

        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

function startVoice(){
    let recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();

    recognition.lang = "en-IN";
    recognition.start();

    recognition.onresult = function(event){
        let transcript = event.results[0][0].transcript;
        input.value = transcript;
        askAI();
    };
}

function downloadNotes(){
    let messages = document.querySelectorAll("#chatBox .message");
    let notes = "";

    messages.forEach(msg => {
        if(msg.classList.contains("user")){
            notes += "Student: " + msg.innerText + "\n\n";
        }

        if(msg.classList.contains("ai") && !msg.classList.contains("thinking")){
            notes += "AI Tutor: " + msg.innerText + "\n\n";
        }
    });

    let blob = new Blob([notes], { type: "text/plain" });

    let a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "AI_Tutor_Notes.txt";
    a.click();
}