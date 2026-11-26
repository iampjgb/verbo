// Verbo · Verse of the day — a home-screen widget for the free Scriptable app (iPhone and iPad).
// Same verse as Verbo's Home each day. Tap the widget to open Verbo at that verse.
// Optional: in the widget's settings, set Parameter to WEB for the World English Bible (default KJV).
const SITE = "https://iampjgb.github.io/verbo/";
const TR = ((args.widgetParameter || "KJV") + "").trim().toUpperCase() === "WEB" ? "WEB" : "KJV";
const DAILY = [["Lamentations 3:22-23", "New Every Morning"], ["Proverbs 3:5-6", "Trust Beyond Understanding"], ["Isaiah 40:31", "Waiting and Strength"], ["Psalms 1:3", "Planted by the Water"], ["Philippians 4:6", "Prayer Instead of Anxiety"], ["Psalms 23:1-2", "The Lord My Shepherd"], ["Psalms 46:10", "Be Still"], ["Joshua 1:9", "Be Strong"], ["Psalms 121:1-2", "Help from the Hills"], ["Matthew 11:28", "Come and Rest"], ["John 8:12", "Light of the World"], ["Psalms 119:105", "A Lamp for My Feet"], ["Isaiah 41:10", "Do Not Fear"], ["Romans 8:28", "All Things for Good"], ["Jeremiah 29:11", "Plans of Peace"], ["Psalms 19:1", "The Heavens Declare"], ["Genesis 15:5", "Count the Stars"], ["Psalms 8:3-4", "What Is Man"], ["Galatians 6:9", "Do Not Grow Weary"], ["John 4:35", "Fields White for Harvest"], ["Psalms 126:5", "Sow in Tears"], ["Psalms 107:29", "He Calms the Storm"], ["Mark 4:39", "Peace, Be Still"], ["Psalms 93:4", "Mightier than the Waves"], ["Isaiah 43:19", "A Way in the Wilderness"], ["Isaiah 35:1", "The Desert Shall Bloom"], ["Psalms 63:1", "Thirsty for God"], ["Psalms 52:8", "Like a Green Olive Tree"], ["John 15:5", "Abide in the Vine"], ["Psalms 92:12", "Flourishing Like a Palm"], ["Psalms 30:5", "Joy in the Morning"], ["Malachi 4:2", "Sun of Righteousness"], ["Psalms 113:3", "From Sunrise to Sunset"], ["Psalms 4:8", "Sleep in Peace"], ["Psalms 91:1", "Under His Shadow"], ["Psalms 18:2", "My Rock"], ["Isaiah 55:10-11", "My Word Will Not Return Empty"], ["Matthew 6:33", "Seek First"], ["Hebrews 12:1", "Run with Endurance"], ["Psalms 42:1", "As the Deer Pants"], ["John 7:38", "Rivers of Living Water"], ["Isaiah 26:3", "Perfect Peace"], ["2 Corinthians 5:17", "A New Creation"], ["1 John 1:5", "God Is Light"], ["Micah 6:8", "Walk Humbly"], ["Psalms 37:5", "Commit Your Way"], ["Matthew 5:14", "A City on a Hill"], ["Psalms 90:12", "Number Our Days"], ["James 1:5", "Ask for Wisdom"], ["Psalms 34:8", "Taste and See"], ["Romans 15:13", "God of Hope"], ["Zephaniah 3:17", "He Rejoices over You"], ["Ecclesiastes 3:1", "A Time for Everything"], ["Habakkuk 3:17-18", "Yet I Will Rejoice"], ["Psalms 139:9-10", "Even There"], ["Isaiah 43:2", "Through the Waters"], ["Nahum 1:7", "A Stronghold"], ["Psalms 16:11", "The Path of Life"], ["Revelation 21:5", "All Things New"], ["Psalms 27:1", "The Lord Is My Light"]];
const BOOKS = ["Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"];
const BLUE = new Color("#1D70B8");

function today() {
  const t = new Date(); t.setHours(12, 0, 0, 0);
  const a = Math.floor((t - new Date(t.getFullYear(), 0, 0)) / 864e5), n = DAILY.length;
  return DAILY[((a + t.getFullYear() * 7) % n + n) % n];
}
function parse(ref) {
  const m = ref.match(/^(.+) (\d+):(\d+)(?:-(\d+))?$/);
  return { book: m[1], bi: BOOKS.indexOf(m[1]), ch: +m[2], v1: +m[3], v2: +(m[4] || m[3]) };
}
async function bookText(bi) {
  const fm = FileManager.local(), dir = fm.joinPath(fm.cacheDirectory(), "verbo"), f = fm.joinPath(dir, TR + "-" + bi + ".json");
  if (!fm.fileExists(dir)) fm.createDirectory(dir, true);
  if (fm.fileExists(f)) { try { return JSON.parse(fm.readString(f)); } catch (e) {} }
  const data = await new Request(SITE + "bible/" + TR.toLowerCase() + "/" + bi + ".json").loadJSON();
  fm.writeString(f, JSON.stringify(data));
  return data;
}
async function build() {
  const [ref, title] = today(), p = parse(ref);
  let text = "";
  try {
    const book = await bookText(p.bi), ch = book[p.ch - 1] || [], vs = [];
    for (let v = p.v1; v <= p.v2; v++) if (ch[v - 1]) vs.push(String(ch[v - 1]).replace(/\s*…:\s.*$/, ""));
    text = vs.join(" ");
  } catch (e) { text = "Open Verbo to read today's verse."; }
  const fam = config.widgetFamily || "medium", max = fam === "small" ? 110 : fam === "large" ? 520 : 230;
  if (text.length > max) text = text.slice(0, max).replace(/\s+\S*$/, "") + "…";
  const dark = Device.isUsingDarkAppearance();
  const w = new ListWidget();
  w.backgroundColor = dark ? new Color("#151918") : Color.white();
  w.setPadding(14, 16, 14, 16);
  w.url = SITE + "?ref=" + encodeURIComponent(ref);
  const top = w.addText(fam === "small" ? "Verse of the day" : "Verse of the day · " + title);
  top.font = Font.semiboldSystemFont(fam === "small" ? 11 : 12); top.textColor = dark ? new Color("#8AB8F0") : BLUE; top.lineLimit = 1;
  w.addSpacer(6);
  const body = w.addText(text);
  body.font = new Font("Georgia", fam === "small" ? 13 : fam === "large" ? 18 : 15);
  body.textColor = dark ? new Color("#E8ECE9") : new Color("#1E2321"); body.minimumScaleFactor = 0.7;
  w.addSpacer();
  const foot = w.addText(ref.replace("-", "–") + " · " + TR);
  foot.font = Font.mediumSystemFont(11); foot.textColor = dark ? new Color("#9AA19C") : new Color("#5E6560");
  const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate() + 1); tomorrow.setHours(0, 5, 0, 0); w.refreshAfterDate = tomorrow;
  return w;
}
const widget = await build();
if (config.runsInWidget) Script.setWidget(widget); else await widget.presentMedium();
Script.complete();
