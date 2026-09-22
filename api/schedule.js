export default async function handler(req, res) {
  if (req.method !== "POST") {
    return res.status(405).json({
      ok: false,
      error: "Method not allowed"
    });
  }

  const qstashToken = process.env.QSTASH_TOKEN;
  const chatgptKey = process.env.CHATGPT_REMINDER_KEY;

  const providedKey =
  req.headers["x-notifier-secret"] ||
  req.query.key;

if (providedKey !== chatgptKey) {
  return res.status(401).json({
    ok: false,
    error: "Unauthorized"
  });
}

  if (!qstashToken || !chatgptKey) {
    return res.status(500).json({
      ok: false,
      error: "Missing environment variables"
    });
  }

  const { text, sendAt } = req.body || {};

  if (!text || !sendAt) {
    return res.status(400).json({
      ok: false,
      error: "text and sendAt are required"
    });
  }

  const sendAtMs = Date.parse(sendAt);

  if (Number.isNaN(sendAtMs)) {
    return res.status(400).json({
      ok: false,
      error: "Invalid sendAt"
    });
  }

  if (sendAtMs <= Date.now()) {
    return res.status(400).json({
      ok: false,
      error: "sendAt must be in the future"
    });
  }

  const unixSeconds = Math.floor(sendAtMs / 1000);

  const destination =
    "https://f1realarmnotificator.vercel.app/api/reminder";

  const qstashUrl =
    `https://qstash.upstash.io/v2/publish/${destination}`;

  const response = await fetch(qstashUrl, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${qstashToken}`,
      "Content-Type": "application/json",
      "Upstash-Not-Before": String(unixSeconds),
      "Upstash-Forward-x-notifier-secret": chatgptKey
    },
    body: JSON.stringify({
      text
    })
  });

  const data = await response.json();

  if (!response.ok) {
    return res.status(500).json({
      ok: false,
      qstash: data
    });
  }

  return res.status(200).json({
    ok: true,
    scheduledFor: new Date(sendAtMs).toISOString(),
    qstash: data
  });
}
