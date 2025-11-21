export const palette = {
  purpleLight: '#A78BFA',
  purplePrimary: '#8B5CF6',
  purpleDark: '#5B21B6',
  
  white: '#FFFFFF',
  offWhite: '#F9FAFB',
  greyLight: '#E5E7EB',
  grey: '#9CA3AF',
  greyDark: '#4B5563',
  black: '#111827',
};

export const lightTheme = {
  background: palette.offWhite,
  card: palette.white,
  text: palette.black,
  textSecondary: palette.greyDark,
  primary: palette.purplePrimary,
  primaryLight: palette.purpleLight,
  borderColor: palette.greyLight,
};

export const darkTheme = {
  background: palette.black,
  card: '#1F2937', // A dark grey for cards
  text: palette.white,
  textSecondary: palette.grey,
  primary: palette.purplePrimary,
  primaryLight: palette.purpleLight,
  borderColor: palette.greyDark,
};