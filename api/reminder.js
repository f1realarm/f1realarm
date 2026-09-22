export default async function handler(req, res) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  const notifierSecret = process.env.NOTIFIER_SECRET;
  const chatgptKey = process.env.CHATGPT_REMINDER_KEY;

  if (!token || !chatId || !notifierSecret || !chatgptKey) {
    return res.status(500).json({
      ok: false,
      error: "Missing environment variables"
    });
  }

  const providedKey =
    req.headers["x-notifier-secret"] ||
    req.query.secret ||
    req.query.key;

  const authorized =
    providedKey === notifierSecret ||
    providedKey === chatgptKey;

  if (!authorized) {
    return res.status(401).json({
      ok: false,
      error: "Unauthorized"
    });
  }

  const text =
    req.body?.text ||
    req.query.text;

  if (!text) {
    return res.status(400).json({
      ok: false,
      error: "Missing text"
    });
  }

  const response = await fetch(
    `https://api.telegram.org/bot${token}/sendMessage`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        chat_id: chatId,
        text
      })
    }
  );

  const data = await response.json();

  return res.status(response.ok ? 200 : 500).json(data);
}
