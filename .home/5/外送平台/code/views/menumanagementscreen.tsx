import React, { useState, useEffect } from 'react';
import { MenuItem } from './MenuItem'; // Assuming MenuItem type is defined elsewhere
import { Button, TextField, Typography, Alert } from '@mui/material';

interface MenuManagementScreenProps {
  // Add any necessary props here
}

const MenuManagementScreen: React.FC<MenuManagementScreenProps> = () => {
  const [menuList, setMenuList] = useState<MenuItem[]>([]);
  const [showAddForm, setShowAddForm] = useState(false);
  const [showEditForm, setShowEditForm] = useState(false);
  const [editMenuItem, setEditMenuItem] = useState<MenuItem | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [error, setError] = useState('');


  const displayMenuList = () => {
    // Fetch menu list from backend API using Axios
    // ... Axios call to fetch menu items ...
    // Example:
    // axios.get('/api/menu').then(response => setMenuList(response.data));
  };

  const showAddMenuForm = () => {
    setShowAddForm(true);
  };

  const showEditMenuForm = (menuItem: MenuItem) => {
    setEditMenuItem(menuItem);
    setShowEditForm(true);
  };

  const handleSave = (menuItem: MenuItem) => {
    // Send data to backend API using Axios
    // ... Axios call to save/update menu item ...
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000); // Hide success message after 3 seconds
  };

  const handleError = (message: string) => {
    setError(message);
    setTimeout(() => setError(''), 3000); // Hide error message after 3 seconds
  };

  useEffect(() => {
    displayMenuList();
  }, []);

  return (
    <div>
      <Button variant="contained" onClick={showAddMenuForm}>Add Menu Item</Button>
      {showAddForm && (
        // Add menu item form here
        <div>
          {/* Form elements */}
          <Button variant="contained" onClick={() => {
            //Handle Add Menu Item Logic
            setShowAddForm(false);
          }}>Save</Button>
        </div>
      )}
      {showEditForm && editMenuItem && (
        // Edit menu item form here
        <div>
          {/* Form elements */}
          <Button variant="contained" onClick={() => {
            handleSave(editMenuItem);
            setShowEditForm(false);
          }}>Save</Button>
        </div>
      )}
      {saveSuccess && <Alert severity="success">Menu item saved successfully!</Alert>}
      {error && <Alert severity="error">{error}</Alert>}
      <Typography variant="h6">Menu List</Typography>
      {menuList.map((item) => (
        <div key={item.id}>
          <MenuItem item={item} onEdit={() => showEditMenuForm(item)} />
        </div>
      ))}
    </div>
  );
};

export default MenuManagementScreen;