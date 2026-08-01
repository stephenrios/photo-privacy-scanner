// Vercel Serverless Function — receives feedback from PhotoPrivacy
// Sends feedback to Feishu (Lark) group via custom bot webhook

const FEISHU_WEBHOOK = process.env.FEISHU_WEBHOOK || '';

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Message required' });
  }

  const timestamp = new Date().toISOString();
  const entry = { email: email || '', message, timestamp };

  // Build Feishu text message
  const feishuBody = {
    msg_type: 'text',
    content: {
      text: `📬 New Feedback from PhotoPrivacy\n\n👤 ${email || 'Anonymous'}\n🕐 ${timestamp}\n\n💬 ${message}`
    }
  };

  // Send to Feishu
  if (FEISHU_WEBHOOK) {
    try {
      const larkRes = await fetch(FEISHU_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feishuBody),
      });
      const larkData = await larkRes.json();
      console.log('📬 Feedback sent to Feishu:', larkData.code === 0 ? 'OK' : larkData.msg);
    } catch (err) {
      console.error('❌ Failed to send to Feishu:', err.message);
    }
  } else {
    console.log('📬 Feedback (no webhook):', JSON.stringify(entry, null, 2));
  }

  res.status(200).json({ success: true });
}
