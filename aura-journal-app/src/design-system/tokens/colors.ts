/**
 * Color Design Tokens
 * Semantic color values for light and dark themes
 */

export interface ColorTokens {
  // Semantic colors
  primary: string;
  secondary: string;
  accent: string;
  background: {
    primary: string;
    secondary: string;
    tertiary: string;
  };
  surface: {
    base: string;
    elevated: string;
    overlay: string;
  };
  text: {
    primary: string;
    secondary: string;
    tertiary: string;
    inverse: string;
  };
  border: {
    subtle: string;
    default: string;
    strong: string;
  };
  status: {
    success: string;
    warning: string;
    error: string;
    info: string;
  };
  // Glassmorphism
  glass: {
    background: string;
    border: string;
    blur: number;
  };
}

export const lightColors: ColorTokens = {
  primary: '#7c3aed',      // Violet-600
  secondary: '#8b5cf6',    // Violet-500
  accent: '#a78bfa',       // Violet-400
  background: {
    primary: '#ffffff',    // White
    secondary: '#f8fafc',  // Slate-50
    tertiary: '#f1f5f9',   // Slate-100
  },
  surface: {
    base: '#ffffff',       // White
    elevated: '#ffffff',   // White with shadow
    overlay: 'rgba(0, 0, 0, 0.5)',
  },
  text: {
    primary: '#0f172a',    // Slate-900
    secondary: '#64748b',  // Slate-500
    tertiary: '#94a3b8',   // Slate-400
    inverse: '#ffffff',    // White
  },
  border: {
    subtle: '#f1f5f9',     // Slate-100
    default: '#e2e8f0',    // Slate-200
    strong: '#cbd5e1',     // Slate-300
  },
  status: {
    success: '#10b981',    // Green-500
    warning: '#f59e0b',    // Amber-500
    error: '#ef4444',      // Red-500
    info: '#3b82f6',       // Blue-500
  },
  glass: {
    background: 'rgba(255, 255, 255, 0.7)',
    border: 'rgba(255, 255, 255, 0.2)',
    blur: 20,
  },
};

export const darkColors: ColorTokens = {
  primary: '#a78bfa',      // Violet-400
  secondary: '#8b5cf6',    // Violet-500
  accent: '#7c3aed',       // Violet-600
  background: {
    primary: '#020617',    // Slate-950
    secondary: '#0f172a',  // Slate-900
    tertiary: '#1e293b',   // Slate-800
  },
  surface: {
    base: '#1e293b',       // Slate-800
    elevated: '#334155',   // Slate-700
    overlay: 'rgba(0, 0, 0, 0.7)',
  },
  text: {
    primary: '#f8fafc',    // Slate-50
    secondary: '#cbd5e1',  // Slate-300
    tertiary: '#94a3b8',   // Slate-400
    inverse: '#0f172a',    // Slate-900
  },
  border: {
    subtle: '#1e293b',     // Slate-800
    default: '#334155',    // Slate-700
    strong: '#475569',     // Slate-600
  },
  status: {
    success: '#34d399',    // Green-400
    warning: '#fbbf24',    // Amber-400
    error: '#f87171',      // Red-400
    info: '#60a5fa',       // Blue-400
  },
  glass: {
    background: 'rgba(30, 41, 59, 0.7)',
    border: 'rgba(255, 255, 255, 0.1)',
    blur: 20,
  },
};
