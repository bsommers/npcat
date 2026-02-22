import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useToast,
  Spinner,
  Center,
} from '@chakra-ui/react';
import CapturePanel from './components/CapturePanel';
import AnalyzePanel from './components/AnalyzePanel';
import TimelinePanel from './components/TimelinePanel';
import FilesPanel from './components/FilesPanel';

function App() {
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetch('/api/version')
      .then(res => res.json())
      .then(data => {
        setLoading(false);
        toast({
          title: 'Connected',
          description: `NetCap Analysis v${data.version}`,
          status: 'success',
          duration: 3000,
        });
      })
      .catch(err => {
        setLoading(false);
        toast({
          title: 'Connection Error',
          description: 'Could not connect to API server',
          status: 'error',
          duration: 5000,
        });
      });
  }, []);

  if (loading) {
    return (
      <Center h="100vh">
        <Spinner size="xl" color="blue.500" />
      </Center>
    );
  }

  return (
    <Box minH="100vh" bg="gray.50">
      <Box bg="blue.600" color="white" py={4} px={8}>
        <Heading size="lg">NetCap Analysis</Heading>
        <Text>Network packet capture and analysis tool</Text>
      </Box>
      
      <Container maxW="container.xl" py={6}>
        <Tabs colorScheme="blue">
          <TabList>
            <Tab>Capture</Tab>
            <Tab>Files</Tab>
            <Tab>Analyze</Tab>
            <Tab>Timeline</Tab>
          </TabList>
          
          <TabPanels>
            <TabPanel>
              <CapturePanel />
            </TabPanel>
            <TabPanel>
              <FilesPanel />
            </TabPanel>
            <TabPanel>
              <AnalyzePanel />
            </TabPanel>
            <TabPanel>
              <TimelinePanel />
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Container>
    </Box>
  );
}

export default App;
