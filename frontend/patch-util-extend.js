const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Find all files in node_modules that use util._extend
const findFiles = () => {
  try {
    // Using grep to find occurrences of util._extend
    const result = execSync(
      "grep -r --include='*.js' 'util\\._extend' node_modules || true",
      { encoding: 'utf8' }
    );

    return result.split('\n')
      .filter(line => line.trim())
      .map(line => {
        const parts = line.split(':');
        return parts[0];
      })
      .filter((value, index, self) => self.indexOf(value) === index); // Remove duplicates
  } catch (error) {
    console.error('Error finding files:', error);
    return [];
  }
};

// Replace util._extend with Object.assign
const patchFiles = (files) => {
  if (files.length === 0) {
    console.log('No files found using util._extend');
    return;
  }

  files.forEach(file => {
    try {
      let content = fs.readFileSync(file, 'utf8');

      // Replace require('util') with a patched version
      if (content.includes("require('util')") || content.includes('require("util")')) {
        content = content.replace(
          /const\s+util\s*=\s*require\(['"]util['"]\)/g,
          `const util = require('util');\nutil._extend = Object.assign;`
        );

        content = content.replace(
          /var\s+util\s*=\s*require\(['"]util['"]\)/g,
          `var util = require('util');\nutil._extend = Object.assign;`
        );
      }

      // Direct replacement of util._extend with Object.assign
      content = content.replace(/util\._extend/g, 'Object.assign');

      fs.writeFileSync(file, content, 'utf8');
      console.log(`Patched ${file}`);
    } catch (error) {
      console.error(`Error patching ${file}:`, error);
    }
  });
};

console.log('Searching for files using util._extend...');
const files = findFiles();
console.log(`Found ${files.length} files to patch`);
patchFiles(files);
console.log('Patching complete');
