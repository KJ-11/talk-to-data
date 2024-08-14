import multer from 'multer';
import path from 'path';
import { NextResponse } from 'next/server';

const upload = multer({
  dest: path.join(process.cwd(), 'uploads'),
  fileFilter: (req, file, cb) => {
    const fileTypes = /csv|xlsx|txt|tsv/;
    const extname = fileTypes.test(path.extname(file.originalname).toLowerCase());
    const mimetype = fileTypes.test(file.mimetype);

    if (extname && mimetype) {
      return cb(null, true);
    } else {
      cb('Error: Only .csv, .xlsx, .txt, and .tsv files are allowed!');
    }
  },
});

export const config = {
  api: {
    bodyParser: false,
  },
};

export async function POST(req) {
  return new Promise((resolve, reject) => {
    upload.single('file')(req, {}, (err) => {
      if (err) {
        console.error(err);
        reject(NextResponse.json({ message: 'File upload failed', error: err }, { status: 500 }));
        return;
      }

      const file = req.file;
      if (file) {
        console.log(`Uploaded file: ${file.originalname}`);
        resolve(NextResponse.json({ message: 'File uploaded successfully', filePath: file.path }, { status: 200 }));
      } else {
        resolve(NextResponse.json({ message: 'No file uploaded' }, { status: 400 }));
      }
    });
  });
}
