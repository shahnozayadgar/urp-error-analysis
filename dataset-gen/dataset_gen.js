// Endpoint api

import 'dotenv/config';
import axios from 'axios';

const url = 'https://api.openai.com/v1/chat/completions';

const res = await axios({
  method: 'post',
  url,
  headers: {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
  },
  data: {
    model: 'gpt-4o-mini',
    max_tokens: 20,
    temperature: 0,
    // prompt: 'Tell me a joke',
    messages: [
      {
        role: 'user',
        content: 'Telle me a joke',
      },
    ],
  },
});
console.log(1, res.data.choices[0].message.content);

// // Node api
import OpenAI from 'openai';

const openai = new OpenAI();

const completion = await openai.chat.completions.create({
  messages: [{ role: 'user', content: 'Tell me a joke' }],
  model: 'gpt-4o-mini',
  temperature: 0.5,
  max_tokens: 150,
});

console.log(2, completion.choices[0].message.content);
