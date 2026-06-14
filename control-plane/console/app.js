const API = "";

function headers() {
  const token = localStorage.getItem("context_skills_token") || "";
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path) {
  const res = await fetch(API + path, { headers: headers() });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

document.getElementById("save-token").onclick = () => {
  localStorage.setItem("context_skills_token", document.getElementById("token").value.trim());
};

document.querySelectorAll("nav button").forEach((btn) => {
  btn.onclick = () => {
    document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
    document.getElementById(`panel-${btn.dataset.panel}`).classList.remove("hidden");
  };
});

document.getElementById("load-skills").onclick = async () => {
  const data = await api("/skills");
  const ul = document.getElementById("skill-list");
  ul.innerHTML = data.map((s) => `<li><strong>${s.name}</strong> — ${s.description}</li>`).join("");
};

document.getElementById("load-usage").onclick = async () => {
  document.getElementById("usage-out").textContent = JSON.stringify(await api("/finops/chargeback"), null, 2);
};

document.getElementById("load-audit").onclick = async () => {
  document.getElementById("audit-out").textContent = JSON.stringify(await api("/audit/events"), null, 2);
};

document.getElementById("load-approvals").onclick = async () => {
  const data = await api("/approvals");
  document.getElementById("approval-list").innerHTML = data.approvals
    .map((a) => `<li>${a.id} — ${a.operation} (${a.status})</li>`)
    .join("");
};

document.getElementById("load-tenants").onclick = async () => {
  document.getElementById("tenants-out").textContent = JSON.stringify(await api("/tenants"), null, 2);
};
