import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Select,
  VStack,
  useToast,
  Progress,
  Text,
  Code,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
} from '@chakra-ui/react';

function AnalyzePanel() {
  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const toast = useToast();

  useEffect(() => {
    fetch('/api/files')
      .then(res => res.json())
      .then(data => {
        setFiles(data.files || []);
        if (data.files && data.files.length > 0) {
          setSelectedFile(data.files[0].name);
        }
      })
      .catch(err => console.error(err));
  }, []);

  const handleAnalyze = async () => {
    if (!selectedFile) {
      toast({
        title: 'No File Selected',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    setAnalyzing(true);
    setReport(null);

    try {
      const filepath = `/tmp/netcap_uploads/${selectedFile}`;
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filepath }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setReport(data.report);
        toast({
          title: 'Analysis Complete',
          status: 'success',
          duration: 3000,
        });
      } else {
        toast({
          title: 'Analysis Failed',
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
      setAnalyzing(false);
    }
  };

  const parseSummary = (reportText) => {
    const lines = reportText.split('\n');
    const summary = {};
    
    lines.forEach(line => {
      if (line.includes('|') && !line.includes('---')) {
        const parts = line.split('|').filter(p => p.trim());
        if (parts.length >= 2) {
          const key = parts[0].trim();
          const value = parts[1].trim();
          if (key && value && !key.includes('Metric')) {
            summary[key] = value;
          }
        }
      }
    });
    
    return summary;
  };

  return (
    <Box p={6} bg="white" borderRadius="md" boxShadow="sm">
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Select PCAP File</FormLabel>
          <Select value={selectedFile} onChange={(e) => setSelectedFile(e.target.value)}>
            {files.map((file) => (
              <option key={file.name} value={file.name}>{file.name}</option>
            ))}
          </Select>
        </FormControl>
        
        {analyzing && <Progress isIndeterminate colorScheme="blue" />}
        
        <Button
          colorScheme="blue"
          onClick={handleAnalyze}
          isLoading={analyzing}
          loadingText="Analyzing..."
          isDisabled={!selectedFile}
        >
          Analyze
        </Button>
        
        {report && (
          <Box>
            <Text fontWeight="bold" mb={2}>Analysis Report:</Text>
            <Code whiteSpace="pre-wrap" p={4} borderRadius="md" bg="gray.100" display="block" maxH="500px" overflowY="auto">
              {report}
            </Code>
          </Box>
        )}
      </VStack>
    </Box>
  );
}

export default AnalyzePanel;
