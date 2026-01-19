import React from 'react';
import { Link, Outlet } from 'react-router-dom';
import { LayoutDashboard, FileSpreadsheet, GraduationCap } from 'lucide-react';

const navigation = [
    // { name: '仪表盘', href: '/', icon: LayoutDashboard }, // Dashboard is redirected to templates for now
    { name: '模板管理', href: '/templates', icon: FileSpreadsheet },
    { name: '试卷批改', href: '/papers', icon: GraduationCap },
];

export function Layout() {
    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-md flex flex-col">
                <div className="p-6 border-b">
                    <h1 className="text-2xl font-bold text-blue-600">Pigai Auto</h1>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    <Link to="/" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors">
                        <LayoutDashboard className="w-5 h-5 mr-3" />
                        Dashboard
                    </Link>
                    <Link to="/templates" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors">
                        <FileSpreadsheet className="w-5 h-5 mr-3" />
                        Templates
                    </Link>
                    <Link to="/papers" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors">
                        <FileText className="w-5 h-5 mr-3" />
                        Exams
                    </Link>
                    <Link to="/grading" className="flex items-center p-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 rounded-lg transition-colors">
                        <CheckSquare className="w-5 h-5 mr-3" />
                        Grading
                    </Link>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto p-8">
                <Outlet />
            </main>
        </div>
    );
}
