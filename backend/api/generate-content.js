import OpenAI from 'openai';
import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
app.use(cors());
app.use(express.json());

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

app.post('/api/generate-content', async (req, res) => {
  try {
    const { brandName, brandDescription, platform, contentType, tone } = req.body;

    const prompt = `Create a ${contentType} for ${brandName} (${brandDescription}) for ${platform} with a ${tone} tone. 
    Include a compelling caption and relevant hashtags. Also provide a detailed image prompt for DALL-E.`;

    const completion = await openai.chat.completions.create({
      messages: [
        {
          role: "system",
          content: "You are a professional social media content creator specializing in brand marketing. Create engaging, platform-specific content that aligns with brand identity."
        },
        {
          role: "user",
          content: prompt
        }
      ],
      model: "gpt-4-turbo-preview",
    });

    const response = completion.choices[0].message.content;
    const [caption, hashtagsStr, imagePrompt] = response.split('\n\n');
    
    const hashtags = hashtagsStr
      .split('#')
      .filter(tag => tag.trim())
      .map(tag => `#${tag.trim()}`);

    res.json({
      caption: caption.trim(),
      hashtags,
      imagePrompt: imagePrompt.trim()
    });
  } catch (error) {
    console.error('Error:', error);
    res.status(500).json({ error: 'Failed to generate content' });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
}); 