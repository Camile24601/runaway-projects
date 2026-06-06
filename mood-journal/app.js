const STORAGE_KEY = "mood-journal-entries";
const SYNC_KEY_STORAGE = "mood-journal-sync-key";
const MOOD_JOURNAL_CONFIG = window.MOOD_JOURNAL_CONFIG || {};
const SUPABASE_URL = MOOD_JOURNAL_CONFIG.supabaseUrl || "";
const SUPABASE_KEY = MOOD_JOURNAL_CONFIG.supabaseKey || "";

const jokes = [
  "今天的烦恼先排队，快乐正在补妆，马上就来。",
  "如果心情有天气预报，那你这里明天大概率转晴，局部还有小甜点。",
  "刚刚有一朵云路过，说它替你背一会儿重东西。",
  "难过像手机低电量，先充一点点温柔，也算重新开机。",
  "你的坏心情已经被我加入待办：稍后处理，优先级下调。"
];

const comforts = [
  "抱抱你。今天已经很努力了，先让自己慢一点也没关系。",
  "给你一个很轻很轻的拥抱，剩下的事可以等你充好电再说。",
  "疲惫不是不够好，是身体在提醒你：该被照顾一下了。",
  "先放下五分钟也可以。喝点水，伸个懒腰，你不用一直撑着。",
  "今天的你值得被温柔对待，哪怕只是早点休息这一件小事。"
];

const form = document.querySelector("#entryForm");
const dateInput = document.querySelector("#entryDate");
const textInput = document.querySelector("#entryText");
const imageInput = document.querySelector("#imageInput");
const imagePreview = document.querySelector("#imagePreview");
const timeline = document.querySelector("#timeline");
const entryCount = document.querySelector("#entryCount");
const latestMood = document.querySelector("#latestMood");
const todayChip = document.querySelector("#todayChip");
const clearFormBtn = document.querySelector("#clearFormBtn");
const clearAllBtn = document.querySelector("#clearAllBtn");
const syncStatus = document.querySelector("#syncStatus");
const syncPasscode = document.querySelector("#syncPasscode");
const connectSyncBtn = document.querySelector("#connectSyncBtn");
const localModeBtn = document.querySelector("#localModeBtn");
const supportDialog = document.querySelector("#supportDialog");
const supportEyebrow = document.querySelector("#supportEyebrow");
const supportTitle = document.querySelector("#supportTitle");
const supportText = document.querySelector("#supportText");
const closeSupportBtn = document.querySelector("#closeSupportBtn");

let currentImage = "";
let entriesCache = [];
let syncKey = localStorage.getItem(SYNC_KEY_STORAGE) || "";
let supabaseClient = null;

function getTodayValue() {
  const today = new Date();
  const offset = today.getTimezoneOffset() * 60000;
  return new Date(today.getTime() - offset).toISOString().slice(0, 10);
}

function formatDate(value) {
  return new Intl.DateTimeFormat("zh-CN", {
    month: "long",
    day: "numeric",
    weekday: "short"
  }).format(new Date(`${value}T00:00:00`));
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
}

function getSupabaseClient() {
  if (supabaseClient) return supabaseClient;
  if (!window.supabase || !SUPABASE_URL || !SUPABASE_KEY) return null;
  supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
  return supabaseClient;
}

async function hashPasscode(value) {
  const text = `mood-journal:${value.trim()}`;
  let hash = 2166136261;

  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, 16777619);
  }

  return `journal-${(hash >>> 0).toString(16).padStart(8, "0")}`;
}

function loadLocalEntries() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
  } catch {
    return [];
  }
}

function saveLocalEntries(entries) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function toEntry(row) {
  return {
    date: row.entry_date,
    mood: row.mood,
    icon: row.icon,
    text: row.body || "",
    image: row.image || "",
    updatedAt: row.updated_at
  };
}

function toRow(entry) {
  return {
    journal_key: syncKey,
    entry_date: entry.date,
    mood: entry.mood,
    icon: entry.icon,
    body: entry.text,
    image: entry.image,
    updated_at: entry.updatedAt
  };
}

async function loadCloudEntries() {
  const client = getSupabaseClient();
  if (!client || !syncKey) return [];

  const { data, error } = await client
    .from("mood_entries")
    .select("entry_date,mood,icon,body,image,updated_at")
    .eq("journal_key", syncKey)
    .order("entry_date", { ascending: false });

  if (error) throw error;
  return data.map(toEntry);
}

async function upsertCloudEntry(entry) {
  const client = getSupabaseClient();
  if (!client || !syncKey) throw new Error("云端同步还没有连接。");

  const { error } = await client
    .from("mood_entries")
    .upsert(toRow(entry), { onConflict: "journal_key,entry_date" });

  if (error) throw error;
}

async function deleteCloudEntry(date) {
  const client = getSupabaseClient();
  if (!client || !syncKey) throw new Error("云端同步还没有连接。");

  const { error } = await client
    .from("mood_entries")
    .delete()
    .eq("journal_key", syncKey)
    .eq("entry_date", date);

  if (error) throw error;
}

async function clearCloudEntries() {
  const client = getSupabaseClient();
  if (!client || !syncKey) throw new Error("云端同步还没有连接。");

  const { error } = await client.from("mood_entries").delete().eq("journal_key", syncKey);
  if (error) throw error;
}

async function connectAndMergeEntries() {
  setSyncStatus("正在连接云端...");

  const localEntries = loadLocalEntries();
  const cloudEntries = await loadCloudEntries();

  if (cloudEntries.length) {
    entriesCache = cloudEntries;
    saveLocalEntries(cloudEntries);
    setSyncStatus("云端同步已连接，已显示这份云端手账。之后点“保存记录”会同步到手机和电脑。", "success");
    renderEntries();
    return;
  }

  if (localEntries.length) {
    await Promise.all(localEntries.map((entry) => upsertCloudEntry(entry)));
    entriesCache = await loadCloudEntries();
    saveLocalEntries(entriesCache);
    setSyncStatus(`云端同步已连接，已首次导入 ${localEntries.length} 条本机记录。`, "success");
    renderEntries();
    return;
  }

  entriesCache = [];
  saveLocalEntries([]);
  setSyncStatus("云端同步已连接。这是一份空手账，点“保存记录”后会同步到手机和电脑。", "success");
  renderEntries();
}

function selectedMood() {
  const checked = document.querySelector("input[name='mood']:checked");
  return {
    name: checked.value,
    icon: checked.dataset.icon
  };
}

function buildEntryFromForm() {
  const mood = selectedMood();

  return {
    date: dateInput.value,
    mood: mood.name,
    icon: mood.icon,
    text: textInput.value.trim(),
    image: currentImage,
    updatedAt: new Date().toISOString()
  };
}

function setSyncStatus(message, tone = "normal") {
  syncStatus.textContent = message;
  syncStatus.dataset.tone = tone;
}

function showImagePreview(src, name = "已选择的照片") {
  currentImage = src;
  imagePreview.innerHTML = `
    <img src="${src}" alt="${escapeHtml(name)}" />
    <div>
      <strong>${escapeHtml(name)}</strong>
      <p>图片会压缩后保存，方便手机和电脑同步。</p>
    </div>
  `;
}

function clearForm() {
  form.reset();
  dateInput.value = getTodayValue();
  currentImage = "";
  imagePreview.innerHTML = "";
}

function randomFrom(items) {
  return items[Math.floor(Math.random() * items.length)];
}

function showSupport({ eyebrow, title, message }) {
  supportEyebrow.textContent = eyebrow;
  supportTitle.textContent = title;
  supportText.textContent = message;

  if (typeof supportDialog.showModal === "function") {
    supportDialog.showModal();
  } else {
    alert(message);
  }
}

function renderEntries() {
  const entries = [...entriesCache].sort((a, b) => b.date.localeCompare(a.date));
  entryCount.textContent = entries.length;
  latestMood.textContent = entries[0]?.mood || "-";

  if (!entries.length) {
    timeline.innerHTML = `<div class="empty-state">还没有记录。写下第一天之后，它会一直留在这里。</div>`;
    return;
  }

  timeline.innerHTML = entries
    .map((entry) => {
      const image = entry.image
        ? `<img class="entry-image" src="${entry.image}" alt="${escapeHtml(entry.date)} 的照片" />`
        : "";
      const text = entry.text ? escapeHtml(entry.text) : "今天没有写文字，但心情已经被好好收下。";

      return `
        <article class="entry-card">
          ${image}
          <div class="entry-body">
            <div class="entry-top">
              <div class="entry-mood">
                <span class="tiny-icon">${entry.icon}</span>
                <span>${escapeHtml(entry.mood)}</span>
              </div>
              <time class="entry-date" datetime="${entry.date}">${formatDate(entry.date)}</time>
            </div>
            <p class="entry-text">${text}</p>
            <button class="delete-entry" type="button" data-date="${entry.date}">删除这天</button>
          </div>
        </article>
      `;
    })
    .join("");
}

async function refreshEntries() {
  if (!syncKey) {
    entriesCache = loadLocalEntries();
    setSyncStatus("本机模式：记录只保存在当前浏览器。");
    renderEntries();
    return;
  }

  setSyncStatus("正在读取云端记录...");

  try {
    entriesCache = await loadCloudEntries();
    setSyncStatus("云端同步已连接：手机和电脑输入同一个暗号即可查看同一份记录。", "success");
  } catch (error) {
    entriesCache = loadLocalEntries();
    setSyncStatus(`云端暂时不可用：${error.message}。当前显示本机记录。`, "error");
  }

  renderEntries();
}

function resizeImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("error", reject);
    reader.addEventListener("load", () => {
      const img = new Image();
      img.addEventListener("error", reject);
      img.addEventListener("load", () => {
        const maxSide = 1280;
        const scale = Math.min(1, maxSide / Math.max(img.width, img.height));
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);

        const context = canvas.getContext("2d");
        context.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.82));
      });
      img.src = reader.result;
    });
    reader.readAsDataURL(file);
  });
}

imageInput.addEventListener("change", async () => {
  const file = imageInput.files?.[0];
  if (!file) return;

  try {
    const src = await resizeImage(file);
    showImagePreview(src, file.name);
  } catch {
    setSyncStatus("图片读取失败，可以换一张再试。", "error");
  }
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const entry = buildEntryFromForm();

  entriesCache = entriesCache.filter((item) => item.date !== entry.date);
  entriesCache.push(entry);
  renderEntries();

  if (syncKey) {
    try {
      await upsertCloudEntry(entry);
      setSyncStatus("已保存到云端。", "success");
    } catch (error) {
      saveLocalEntries(entriesCache);
      setSyncStatus(`云端保存失败：${error.message}。已先保存在本机。`, "error");
    }
  } else {
    saveLocalEntries(entriesCache);
  }

  if (entry.mood === "悲伤") {
    showSupport({
      eyebrow: "给难过的你",
      title: "先收下一个小笑话",
      message: randomFrom(jokes)
    });
  }

  if (entry.mood === "疲惫") {
    showSupport({
      eyebrow: "给累累的你",
      title: "先收下一个小安慰",
      message: randomFrom(comforts)
    });
  }
});

timeline.addEventListener("click", async (event) => {
  const button = event.target.closest(".delete-entry");
  if (!button) return;

  entriesCache = entriesCache.filter((entry) => entry.date !== button.dataset.date);
  renderEntries();

  if (syncKey) {
    try {
      await deleteCloudEntry(button.dataset.date);
      setSyncStatus("已从云端删除这天记录。", "success");
    } catch (error) {
      setSyncStatus(`云端删除失败：${error.message}`, "error");
    }
  } else {
    saveLocalEntries(entriesCache);
  }
});

clearFormBtn.addEventListener("click", clearForm);

clearAllBtn.addEventListener("click", async () => {
  if (!confirm("确定要清除所有心情记录吗？")) return;

  entriesCache = [];
  renderEntries();

  if (syncKey) {
    try {
      await clearCloudEntries();
      setSyncStatus("已清除这份云端手账。", "success");
    } catch (error) {
      setSyncStatus(`云端清除失败：${error.message}`, "error");
    }
  } else {
    localStorage.removeItem(STORAGE_KEY);
  }
});

connectSyncBtn.addEventListener("click", async () => {
  const passcode = syncPasscode.value.trim();
  if (!passcode) {
    setSyncStatus("先输入一个同步暗号。手机和电脑使用同一个暗号即可同步。", "error");
    return;
  }

  if (!getSupabaseClient()) {
    setSyncStatus("Supabase 脚本没有加载成功，请检查网络后刷新。", "error");
    return;
  }

  syncKey = await hashPasscode(passcode);
  localStorage.setItem(SYNC_KEY_STORAGE, syncKey);

  try {
    await connectAndMergeEntries();
  } catch (error) {
    syncKey = "";
    localStorage.removeItem(SYNC_KEY_STORAGE);
    setSyncStatus(`云端连接失败：${error.message}`, "error");
  }
});

localModeBtn.addEventListener("click", async () => {
  syncKey = "";
  syncPasscode.value = "";
  localStorage.removeItem(SYNC_KEY_STORAGE);
  await refreshEntries();
});

closeSupportBtn.addEventListener("click", () => supportDialog.close());

todayChip.textContent = formatDate(getTodayValue());
dateInput.value = getTodayValue();
refreshEntries();
