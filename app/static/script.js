// Mock dữ liệu tài liệu
const documents = [
  {id:1, title:"Hợp đồng A", type:"Hợp đồng", content:"Nội dung hợp đồng A..."},
  {id:2, title:"Hồ sơ vụ án B", type:"Hồ sơ", content:"Chi tiết vụ án B..."},
  {id:3, title:"Quyết định C", type:"Quyết định", content:"Nội dung quyết định C..."}
];

// Mock phân quyền (luật sư chỉ thấy doc id 1,2)
const userDocs = [1,2];

const docList = document.getElementById("doc-list");
const docDetail = document.getElementById("doc-detail");

// Load dashboard
documents.forEach(doc => {
  if(userDocs.includes(doc.id)){
    const li = document.createElement("li");
    li.textContent = doc.title + " - " + doc.type;
    li.style.cursor = "pointer";
    li.onclick = () => showDetail(doc);
    docList.appendChild(li);
  }
});

function showDetail(doc){
  docDetail.innerHTML = `<h3>${doc.title}</h3>
                         <p><i>${doc.type}</i></p>
                         <div>${doc.content}</div>`;
}

// Chatbot logic
const chatInput = document.getElementById("chat-input");
const chatSend = document.getElementById("chat-send");
const chatMessages = document.getElementById("chat-messages");

chatSend.onclick = () => {
  const msg = chatInput.value.trim();
  if(!msg) return;
  addMessage(msg,"user");
  // Mock phản hồi RAG
  setTimeout(() => addMessage("Bot trả lời dựa trên RAG: Nội dung liên quan đến '"+msg+"'", "bot"), 500);
  chatInput.value = "";
};

function addMessage(text, from){
  const div = document.createElement("div");
  div.textContent = text;
  div.className = from;
  chatMessages.appendChild(div);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}
