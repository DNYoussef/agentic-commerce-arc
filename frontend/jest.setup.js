require('@testing-library/jest-dom');

const { TextDecoder, TextEncoder } = require('util');

global.TextEncoder = TextEncoder;
global.TextDecoder = TextDecoder;

// Import the jest-setup library for mocks and matchers
// Note: The full setup is available via:
// import { setupMocks, configure } from '@testing/setup';
// import { render, screen } from '@testing/test-utils';
// import { matchers } from '@testing/matchers';

// Auto-register custom matchers
const { matchers } = require('./src/lib/testing/matchers');
expect.extend(matchers);
