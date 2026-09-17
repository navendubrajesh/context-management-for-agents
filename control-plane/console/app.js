const API = "";
let chargebackRows = [];

function headers() {
  const token = localStorage.getItem("context_skills_token") || "";
  return token ? { Authorization: `Bearer ${token}`, "Content-Type": "application/json" } : { "Content-Type": "application/json" };
}

async function api(path, options = {}) {
  const res = await fetch(API + path, { ...options, headers: { ...headers(), ...(options.headers || {}) } });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  if (res.status === 204) return null;
  return res.json();
}

async function bootstrapSession() {
  try {
    const session = await fetch("/console/auth/session", { credentials: "include" });
    if (session.ok) {
      const data = await session.json();
      localStorage.setItem("context_skills_token", data.token);
      document.getElementById("sso-logout").classList.remove("hidden");
    }
  } catch (_) {
    /* not logged in */
  }
}

document.getElementById("sso-login").onclick = () => {
  window.location.href = "/console/auth/login";
};

document.getElementById("sso-logout").onclick = async () => {
  await fetch("/console/auth/logout", { method: "POST", credentials: "include" });
  localStorage.removeItem("context_skills_token");
  window.location.reload();
};

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
  ul.innerHTML = data
    .map((s) => {
      const stale = s.stale ? `<span class="stale-badge">stale</span>` : "";
      return `<li class="${s.stale ? "stale-skill" : ""}"><strong>${s.name}</strong> — ${s.description} ${stale}</li>`;
    })
    .join("");
};

document.getElementById("load-usage").onclick = async () => {
  const from = document.getElementById("chargeback-from").value;
  const to = document.getElementById("chargeback-to").value;
  const params = new URLSearchParams();
  if (from) params.set("date_from", from);
  if (to) params.set("date_to", to);
  const data = await api(`/finops/chargeback?${params.toString()}`);
  chargebackRows = data.tenants || [];
  const tbody = document.querySelector("#chargeback-table tbody");
  tbody.innerHTML = chargebackRows
    .map(
      (row) =>
        `<tr><td>${row.tenant_id}</td><td>${row.operations}</td><td>${row.tokens_saved}</td><td>${row.est_cost_usd}</td></tr>`
    )
    .join("");
};

document.getElementById("export-csv").onclick = () => {
  const lines = ["tenant_id,operations,tokens_saved,est_cost_usd"];
  chargebackRows.forEach((row) => {
    lines.push(`${row.tenant_id},${row.operations},${row.tokens_saved},${row.est_cost_usd}`);
  });
  const blob = new Blob([lines.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "chargeback.csv";
  a.click();
  URL.revokeObjectURL(url);
};

document.getElementById("load-efficiency").onclick = async () => {
  const data = await api("/metrics/efficiency");
  document.getElementById("efficiency-summary").innerHTML = `
    <p><strong>Savings:</strong> ${data.savings_pct}% (${data.tokens_saved} tokens)</p>
    <p><strong>Cost per operation:</strong> $${data.cost_per_operation_usd}</p>
    <p><strong>Operations:</strong> ${data.operations}</p>`;
};

document.getElementById("load-audit").onclick = async () => {
  document.getElementById("audit-out").textContent = JSON.stringify(await api("/audit/events"), null, 2);
};

document.getElementById("load-approvals").onclick = async () => {
  const data = await api("/approvals");
  document.getElementById("approval-list").innerHTML = data.approvals
    .map(
      (a) =>
        `<li>${a.id} — ${a.operation} (${a.status})
          <button data-id="${a.id}" data-approve="true">Approve</button>
          <button data-id="${a.id}" data-approve="false">Reject</button>
          <a href="#" data-audit="${a.id}">Audit trail</a>
        </li>`
    )
    .join("");
  document.querySelectorAll("#approval-list button").forEach((btn) => {
    btn.onclick = async () => {
      await api(`/approvals/${btn.dataset.id}/decide`, {
        method: "POST",
        body: JSON.stringify({ approve: btn.dataset.approve === "true", reason: "console decision" }),
      });
      document.getElementById("load-approvals").click();
    };
  });
  document.querySelectorAll("#approval-list a[data-audit]").forEach((link) => {
    link.onclick = async (event) => {
      event.preventDefault();
      const events = await api("/audit/events");
      document.getElementById("audit-out").textContent = JSON.stringify(events, null, 2);
      document.querySelector('[data-panel="audit"]').click();
    };
  });
};

document.getElementById("approval-form").onsubmit = async (event) => {
  event.preventDefault();
  const operation = document.getElementById("approval-operation").value.trim();
  const skill = document.getElementById("approval-skill").value.trim();
  await api("/approvals", {
    method: "POST",
    body: JSON.stringify({ operation, payload: { skill } }),
  });
  document.getElementById("load-approvals").click();
};

document.getElementById("load-tenants").onclick = async () => {
  document.getElementById("tenants-out").textContent = JSON.stringify(await api("/tenants"), null, 2);
};

document.getElementById("load-tenant-admin").onclick = async () => {
  const data = await api("/tenant-admin/overview");
  const usage = data.usage || {};
  document.getElementById("tenant-admin-quota").innerHTML = `
    <p><strong>Tenant:</strong> ${data.tenant.name} (${data.tenant.tenant_id})</p>
    <p><strong>Quota:</strong> ${usage.tokens_used || 0} / ${usage.token_limit || 0} tokens (${usage.used_pct || 0}%)</p>`;
  document.getElementById("tenant-skills").value = (data.tenant.enabled_skills || []).join(", ");
  document.getElementById("tenant-users").innerHTML = (data.users || [])
    .map((u) => `<li>${u.userName} — ${(u.roles || []).join(", ")}</li>`)
    .join("");
};

document.getElementById("save-tenant-skills").onclick = async () => {
  const raw = document.getElementById("tenant-skills").value;
  const enabled_skills = raw.split(",").map((s) => s.trim()).filter(Boolean);
  await api("/tenant-admin/skills", { method: "PATCH", body: JSON.stringify({ enabled_skills }) });
  document.getElementById("load-tenant-admin").click();
};

document.getElementById("invite-form").onsubmit = async (event) => {
  event.preventDefault();
  await api("/tenant-admin/users/invite", {
    method: "POST",
    body: JSON.stringify({
      email: document.getElementById("invite-email").value.trim(),
      display_name: document.getElementById("invite-name").value.trim(),
      roles: ["viewer"],
    }),
  });
  document.getElementById("load-tenant-admin").click();
};

bootstrapSession();
