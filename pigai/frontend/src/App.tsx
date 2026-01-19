import React from 'react';
import { createBrowserRouter, RouterProvider, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import TemplateList from './pages/TemplateList';
import TemplateCreate from './pages/TemplateCreate';
import TemplateEditor from './pages/TemplateEditor';
import PaperList from './pages/PaperList';
import PaperUpload from './pages/PaperUpload';
import PaperResult from './pages/PaperResult';

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        path: '/',
        element: <Navigate to="/templates" replace />,
      },
      {
        path: 'templates',
        element: <TemplateList />,
      },
      {
        path: 'templates/new',
        element: <TemplateCreate />,
      },
      {
        path: 'templates/:id/edit',
        element: <TemplateEditor />,
      },
      {
        path: 'papers',
        element: <PaperList />,
      },
      {
        path: 'papers/upload',
        element: <PaperUpload />,
      },
      {
        path: 'papers/:id',
        element: <PaperResult />,
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}

export default App;
