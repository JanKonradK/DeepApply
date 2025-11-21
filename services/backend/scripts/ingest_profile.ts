import dotenv from 'dotenv';
import fs from 'fs/promises';
import path from 'path';
import { storeEmbedding } from '../src/services/rag';

dotenv.config();

const PROFILE_DATA_DIR = path.resolve(__dirname, '../../../profile_data');

async function ingestFiles() {
    console.log(`Scanning ${PROFILE_DATA_DIR} for profile data...`);

    try {
        await fs.access(PROFILE_DATA_DIR);
    } catch {
        console.error(`Directory ${PROFILE_DATA_DIR} does not exist. Please create it and add .md or .txt files.`);
        process.exit(1);
    }

    const files = await fs.readdir(PROFILE_DATA_DIR);
    const textFiles = files.filter(f => f.endsWith('.md') || f.endsWith('.txt'));

    if (textFiles.length === 0) {
        console.log('No text files found to ingest.');
        return;
    }

    for (const file of textFiles) {
        console.log(`Processing ${file}...`);
        const content = await fs.readFile(path.join(PROFILE_DATA_DIR, file), 'utf-8');

        // Simple chunking by paragraphs
        const chunks = content.split('\n\n').filter(c => c.trim().length > 0);

        for (const chunk of chunks) {
            if (chunk.trim().length < 20) continue; // Skip very short chunks
            await storeEmbedding(chunk.trim(), file);
            process.stdout.write('.');
        }
        console.log('\nDone.');
    }
    console.log('Ingestion complete.');
    process.exit(0);
}

ingestFiles().catch(console.error);
