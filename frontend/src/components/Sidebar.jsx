import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, MessageSquare, Files, BarChart3, LogOut, Menu, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { useAuth, useUser } from '@clerk/clerk-react';

const ADMIN_EMAILS = ["worshipgate1@gmail.com", "shivam@theaffordableorganicstore.com", "naiknikhil248@gmail.com"];

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { signOut } = useAuth();
  const { user } = useUser();

  const userEmail = user?.primaryEmailAddress?.emailAddress;
  const isAdmin = userEmail && ADMIN_EMAILS.includes(userEmail);

  const toggleSidebar = () => setIsOpen(!isOpen);
  const closeSidebar = () => setIsOpen(false);
  const toggleCollapse = (e) => {
    e.stopPropagation();
    setIsCollapsed(!isCollapsed);
  };

  return (
    <>
      <button className="mobile-toggle" onClick={toggleSidebar}>
        {isOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {isOpen && <div className="sidebar-overlay" onClick={closeSidebar} />}

      <div className={`sidebar ${isOpen ? 'open' : ''} ${isCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          {!isCollapsed && <h1>Chatbot Admin</h1>}
          <button className="collapse-btn" onClick={toggleCollapse} title={isCollapsed ? "Expand Sidebar" : "Collapse Sidebar"}>
            {isCollapsed ? <ChevronRight size={18} /> : <ChevronLeft size={18} />}
          </button>
        </div>
        
        <nav className="sidebar-nav">
          {isAdmin && (
            <NavLink to="/dashboard" title="Dashboard" onClick={closeSidebar} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
              <LayoutDashboard size={20} />
              {!isCollapsed && <span>Admin Dashboard</span>}
            </NavLink>
          )}
          <NavLink to="/chat" title="Chat" onClick={closeSidebar} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
            <MessageSquare size={20} />
            {!isCollapsed && <span>Chat</span>}
          </NavLink>
          {isAdmin && (
            <>
              <NavLink to="/documents" title="Knowledge Base" onClick={closeSidebar} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                <Files size={20} />
                {!isCollapsed && <span>Knowledge Base</span>}
              </NavLink>
              <NavLink to="/analytics" title="Analytics" onClick={closeSidebar} className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
                <BarChart3 size={20} />
                {!isCollapsed && <span>Analytics</span>}
              </NavLink>
            </>
          )}
        </nav>

        <div className="sidebar-footer">
          {!isCollapsed && user && (
            <div className="sidebar-user" title={user.primaryEmailAddress?.emailAddress}>
              {user.primaryEmailAddress?.emailAddress}
            </div>
          )}
          <button onClick={() => signOut()} className="logout-btn" title="Logout">
            <LogOut size={18} />
            {!isCollapsed && <span>Logout</span>}
          </button>
        </div>
      </div>
    </>
  );
};

export default Sidebar;
