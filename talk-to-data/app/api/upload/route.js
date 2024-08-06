import multer from 'multer';
import path from 'path';
import { NextResponse } from 'next/server';

const upload = multer({
  dest: path.join(process.cwd(), 'uploads'),
});

export const config = {
  api: {
    bodyParser: false, // Disallow body parsing, consume as stream
  },
};

export async function POST(req) {
  return new Promise((resolve, reject) => {
    upload.single('file')(req, {}, (err) => {
      if (err) {
        console.error(err);
        reject(NextResponse.json({ message: 'File upload failed' }, { status: 500 }));
        return;
      }

      const file = req.file;
      if (file) {
        console.log(`Uploaded file: ${file.originalname}`);
        resolve(NextResponse.json({ message: 'File uploaded successfully' }, { status: 200 }));
      } else {
        resolve(NextResponse.json({ message: 'No file uploaded' }, { status: 400 }));
      }
    });
  });
}
