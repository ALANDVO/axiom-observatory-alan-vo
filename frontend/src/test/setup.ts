import '@testing-library/jest-dom';

// Polyfill or stub URL.createObjectURL if necessary in jsdom
if (typeof window.URL.createObjectURL === 'undefined') {
  window.URL.createObjectURL = () => 'blob:mock-url';
  window.URL.revokeObjectURL = () => {};
}
