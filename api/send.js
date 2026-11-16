export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Faqat POST ruxsat etilgan' });
  }

  const { chatId, message } = req.body;
  const TOKEN = process.env.TELEGRAM_BOT_TOKEN;

  try {
    const response = await fetch(`https://api.telegram.org/bot${TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: 'HTML'
      })
    });

    const data = await response.json();
    if (data.ok) {
      return res.status(200).json({ success: true });
    } else {
      return res.status(400).json({ success: false, error: data.description });
    }
  } catch (error) {
    return res.status(500).json({ success: false, error: error.message });
  }
}
