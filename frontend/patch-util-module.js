// This script patches the util module to replace _extend with Object.assign
const originalUtil = require('util');

// Replace util._extend with Object.assign
if (originalUtil && typeof originalUtil._extend === 'function') {
  originalUtil._extend = Object.assign;
  console.log('✅ Successfully patched util._extend with Object.assign');
} else {
  console.log('❌ Could not patch util._extend (not found)');
} 