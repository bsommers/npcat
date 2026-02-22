import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
  useToast,
  Progress,
  Text,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';

function CapturePanel() {
  const [interface_, setInterface] = useState('');
  const [count, setCount] = useState(100);
  const [filter, setFilter] = useState('');
  const [duration, setDuration] = useState('');
  const [capturing, setCapturing] = useState(false);
  const [interfaces, setInterfaces] = useState([]);
  const toast = useToast();

  useEffect(() => {
    fetch('/api/interfaces')
      .then(res => res.json())
      .then(data => {
        setInterfaces(data.interfaces || []);
        if (data.interfaces && data.interfaces.length > 0) {
          setInterface(data.interfaces[0]);
        }
      })
      .catch(() => {
        setInterfaces(['eth0', 'wlan0', 'lo']);
      });
  }, []);

  const handleCapture = async () => {
    setCapturing(true);
    
    try {
      const response = await fetch('/api/capture', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interface: interface_,
          count: parseInt(count),
          filter: filter,
          duration: duration ? parseInt(duration) : null,
        }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast({
          title: 'Capture Complete',
          description: `Saved to ${data.filename}`,
          status: 'success',
          duration: 5000,
        });
      } else {
        toast({
          title: 'Capture Failed',
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
      setCapturing(false);
    }
  };

  return (
    <Box p={6} bg="white" borderRadius="md" boxShadow="sm">
      <VStack spacing={4} align="stretch">
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          Live capture requires root privileges. The server must be running with appropriate permissions.
        </Alert>
        
        <FormControl>
          <FormLabel>Network Interface</FormLabel>
          <Select value={interface_} onChange={(e) => setInterface(e.target.value)}>
            {interfaces.map((iface) => (
              <option key={iface} value={iface}>{iface}</option>
            ))}
          </Select>
        </FormControl>
        
        <FormControl>
          <FormLabel>Packet Count</FormLabel>
          <Input
            type="number"
            value={count}
            onChange={(e) => setCount(e.target.value)}
            placeholder="100"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>BPF Filter (optional)</FormLabel>
          <Input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            placeholder="e.g., tcp port 80"
          />
        </FormControl>
        
        <FormControl>
          <FormLabel>Duration (seconds, optional)</FormLabel>
          <Input
            type="number"
            value={duration}
            onChange={(e) => setDuration(e.target.value)}
            placeholder="Leave empty for packet count"
          />
        </FormControl>
        
        {capturing && <Progress isIndeterminate colorScheme="blue" />}
        
        <Button
          colorScheme="blue"
          onClick={handleCapture}
          isLoading={capturing}
          loadingText="Capturing..."
        >
          Start Capture
        </Button>
      </VStack>
    </Box>
  );
}

export default CapturePanel;
