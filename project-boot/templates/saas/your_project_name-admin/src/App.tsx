import { FC } from 'react';
import Router from '@/router';
import ThemeProvider from '@/providers/ThemeProvider';
import '@/assets/styles/global.scss';

const App: FC = () => {
  return (
    <ThemeProvider>
      <Router />
    </ThemeProvider>
  );
};

export default App;
