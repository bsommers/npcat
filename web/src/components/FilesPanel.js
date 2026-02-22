import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  useToast,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  IconButton,
  Input,
} from '@chakra-ui/react';
import { DeleteIcon, DownloadIcon } from '@chakra-ui/icons';

function FilesPanel() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const toast = useToast();

  const loadFiles = () => {
    fetch('/api/files')
      .then(res => res.json())
      .then(data => setFiles(data.files || []))
      .catch(err => console.error(err));
  };

  useEffect(() => {
    loadFiles();
  }, []);

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast({
          title: 'Upload Complete',
          description: data.filename,
          status: 'success',
          duration: 3000,
        });
        loadFiles();
      } else {
        toast({
          title: 'Upload Failed',
          description: data.error,
          status: 'error',
          duration: 5000,
        });
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err.message,
        status: 'error',
        duration: 5000,
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (filename) => {
    try {
      const response = await fetch(`/api/files/${filename}`, {
        method: 'DELETE',
      });
      
      if (response.ok) {
        toast({
          title: 'Deleted',
          status: 'success',
          duration: 2000,
        });
        loadFiles();
      }
    } catch (err) {
      toast({
        title: 'Error',
        description: err.message,
        status: 'error',
        duration: 5000,
      });
    }
  };

  const formatSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <Box p={6} bg="white" borderRadius="md" boxShadow="sm">
      <VStack spacing={4} align="stretch">
        <HStack>
          <Input
            type="file"
            accept=".pcap,.pcapng,.cap"
            onChange={handleUpload}
            display="none"
            id="pcap-upload"
          />
          <Button
            as="label"
            htmlFor="pcap-upload"
            colorScheme="blue"
            isLoading={uploading}
            cursor="pointer"
          >
            Upload PCAP File
          </Button>
        </HStack>
        
        <Table variant="simple" size="sm">
          <Thead>
            <Tr>
              <Th>Filename</Th>
              <Th>Size</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          <Tbody>
            {files.length === 0 ? (
              <Tr>
                <Td colSpan={3} textAlign="center">No files uploaded</Td>
              </Tr>
            ) : (
              files.map((file) => (
                <Tr key={file.name}>
                  <Td>
                    <Badge colorScheme="blue">{file.name.split('.')[1]}</Badge>
                    {' '}
                    {file.name}
                  </Td>
                  <Td>{formatSize(file.size)}</Td>
                  <Td>
                    <IconButton
                      icon={<DeleteIcon />}
                      size="sm"
                      colorScheme="red"
                      variant="ghost"
                      onClick={() => handleDelete(file.name)}
                      aria-label="Delete"
                    />
                  </Td>
                </Tr>
              ))
            )}
          </Tbody>
        </Table>
      </VStack>
    </Box>
  );
}

export default FilesPanel;
