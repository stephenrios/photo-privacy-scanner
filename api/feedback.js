// Vercel Serverless Function — receives feedback from PhotoPrivacy
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { email, message } = req.body;
  if (!message) {
    return res.status(400).json({ error: 'Message required' });
  }

  const entry = {
    email: email || '',
    message,
    timestamp: new Date().toISOString(),
  };

  // In production, forward to Lark / email / database
  console.log('📬 Feedback:', JSON.stringify(entry, null, 2));

  res.status(200).json({ success: true });
}
