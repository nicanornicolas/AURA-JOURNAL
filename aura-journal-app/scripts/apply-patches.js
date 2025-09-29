import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const screenJsPath = path.resolve(
  __dirname,
  '../node_modules/@react-navigation/elements/lib/module/Screen.js'
);

let screenJsContent = fs.readFileSync(screenJsPath, 'utf8');

screenJsContent = screenJsContent.replace(
  'pointerEvents: "box-none",',
  'style: [styles.header, headerTransparent ? styles.absolute : null, { pointerEvents: "box-none" }],'
);

fs.writeFileSync(screenJsPath, screenJsContent, 'utf8');

console.log('Successfully patched @react-navigation/elements/lib/module/Screen.js');