```typescript
import React, { useState } from 'react';
import { TextField, Button, Box, Typography } from '@mui/material';
import axios from 'axios';

interface AddEditMenuFormProps {
  initialMenu?: {
    menuName?: string;
    price?: number;
    image?: string; // Assuming image is stored as a URL
    description?: string;
  };
  onSubmit: (menu: { menuName: string; price: number; image: string; description: string }) => void;
}

const AddEditMenuForm: React.FC<AddEditMenuFormProps> = ({ initialMenu, onSubmit }) => {
  const [menuName, setMenuName] = useState(initialMenu?.menuName || '');
  const [price, setPrice] = useState(initialMenu?.price || 0);
  const [image, setImage] = useState(initialMenu?.image || '');
  const [description, setDescription] = useState(initialMenu?.description || '');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ menuName, price, image, description });
  };

  return (
    <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
      <TextField
        margin="normal"
        required
        fullWidth
        id="menuName"
        label="Menu Name"
        name="menuName"
        autoComplete="menuName"
        autoFocus
        value={menuName}
        onChange={(e) => setMenuName(e.target.value)}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        id="price"
        label="Price"
        type="number"
        name="price"
        autoComplete="price"
        value={price}
        onChange={(e) => setPrice(parseFloat(e.target.value))}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        id="image"
        label="Image URL"
        name="image"
        autoComplete="image"
        value={image}
        onChange={(e) => setImage(e.target.value)}
      />
      <TextField
        margin="normal"
        required
        fullWidth
        id="description"
        label="Description"
        name="description"
        autoComplete="description"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
      />
      <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>
        Submit
      </Button>
    </Box>
  );
};

export default AddEditMenuForm;