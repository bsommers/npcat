import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  VStack,
  useToast,
  Progress,
  Code,
  Checkbox,
  CheckboxGroup,
  Wrap,
  WrapItem,
} from '@chakra-ui/react';

function TimelinePanel() {
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [report, setReport] = useState(null);
  const toast = useToast();

  useEffect(() => {
    fetch('/api/files')
      .then(res => res.json())
      .then(data => setFiles(data.files || []))
      .catch(err => console.error(err));
  }, []);

  const handleFileToggle = (filename) => {
    setSelectedFiles(prev => 
      prev.includes(filename)
        ? prev.filter(f => f !== filename)
        : [...prev, filename]
    );
  };

  const handleTimeline = async () => {
    if (selectedFiles.length < 2) {
      toast({
        title: 'Select at least 2 files',
        description: 'Timeline requires multiple capture files',
        status: 'warning',
        duration: 3000,
      });
      return;
    }

    setAnalyzing(true);
    setReport(null);

    try {
      const filepaths = selectedFiles.map(f => `/tmp/netcap_uploads/${f}`);
      
      const response = await fetch('/api/timeline', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filepaths }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setReport(data.report);
        toast({
          title: 'Timeline Analysis Complete',
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

  return (
    <Box p={6} bg="white" borderRadius="md" boxShadow="sm">
      <VStack spacing={4} align="stretch">
        <FormControl>
          <FormLabel>Select Multiple PCAP Files (2+ for timeline)</FormLabel>
          <CheckboxGroup value={selectedFiles}>
            <Wrap spacing={3}>
              {files.length === 0 ? (
                <WrapItem>No files available. Upload files first.</WrapItem>
              ) : (
                files.map((file) => (
                  <WrapItem key={file.name}>
                    <Checkbox
                      value={file.name}
                      onChange={() => handleFileToggle(file.name)}
                    >
                      {file.name}
                    </Checkbox>
                  </WrapItem>
                ))
              )}
            </Wrap>
          </CheckboxGroup>
        </FormControl>
        
        {analyzing && <Progress isIndeterminate colorScheme="blue" />}
        
        <Button
          colorScheme="blue"
          onClick={handleTimeline}
          isLoading={analyzing}
          loadingText="Analyzing Timeline..."
          isDisabled={selectedFiles.length < 2}
        >
          Generate Timeline
        </Button>
        
        {report && (
          <Box>
            <Code whiteSpace="pre-wrap" p={4} borderRadius="md" bg="gray.100" display="block" maxH="500px" overflowY="auto">
              {report}
            </Code>
          </Box>
        )}
      </VStack>
    </Box>
  );
}

export default TimelinePanel;
