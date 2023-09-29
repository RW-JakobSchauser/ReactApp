import './App.css';
import * as React from 'react'


// 1. import `ChakraProvider` component
import { Center, ChakraProvider, HStack, VStack, Heading } from '@chakra-ui/react'
import { Card, CardHeader, CardBody, CardFooter } from '@chakra-ui/react'
import { Image, Button } from '@chakra-ui/react'
import { SimpleGrid, Flex, Spacer } from "@chakra-ui/react"
import { IconButton } from '@chakra-ui/react'
import { CloseIcon } from '@chakra-ui/icons'
import { Select } from '@chakra-ui/react'
import { Drawer, DrawerBody, DrawerFooter, DrawerHeader, DrawerOverlay, DrawerContent, DrawerCloseButton } from '@chakra-ui/react'
import { useDisclosure } from '@chakra-ui/react'
import { Checkbox, CheckboxGroup, Stack } from "@chakra-ui/react"
import Plot from 'react-plotly.js';
import { Divider } from "@chakra-ui/react"
import {Box} from "@chakra-ui/react"
import { AbsoluteCenter } from '@chakra-ui/react';
import theme from './theme'


const col = "#c6000e"

function App() {


  return (
    <ChakraProvider theme = {theme}>
      <MyApp />
    </ChakraProvider>
  )
}

function DrawerModule({checkedItems, setCheckedItems, models}) {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const btnRef = React.useRef()

  const num_models = checkedItems.filter((c) => c).length;

  function handleCheck(index){
    const newArr = checkedItems.slice()
    newArr[index] = !newArr[index]
    setCheckedItems(newArr)
  }

  function deployModels(){
    console.log(checkedItems)
    console.log(models)
  }

  return (
    <>
      <Button size="lg" ref={btnRef} color = "#FFFFFF" textColor = {col}  onClick={onOpen} alignSelf="flex-start">
        {/* {num_models > 0? "Click to select/deselect models": "No models selected" } */}
        Select/deselect models
      </Button>
      <Drawer
        isOpen={isOpen}
        placement='left'
        onClose={onClose}
        finalFocusRef={btnRef}
      >
        <DrawerOverlay />
        <DrawerContent>
          {/* <DrawerCloseButton /> */}
          <DrawerHeader bg = {col} textColor="white">Select the models to deploy </DrawerHeader>
          <DrawerBody>
            {/* add space */}
            <Box height = "10px"/>

          <CheckboxGroup colorScheme= "ROCKWOOL" defaultValue={['naruto', 'kakashi']}>

            <Stack spacing={5} direction='column'>
              {models.map((model, index) => {
                return <Checkbox isChecked = {checkedItems[index]} onChange = {() => handleCheck(index)} size = "lg"> {model} </Checkbox>
              })}
            </Stack>
          </CheckboxGroup>
          </DrawerBody>

          <DrawerFooter>
            <Button variant='outline' mr={3} onClick={onClose}>
              Close
            </Button>
          </DrawerFooter>
        </DrawerContent>
      </Drawer>
    </>
  )
}

function MyApp() {
    const [checkedItems, setCheckedItems] = React.useState([false, false, false, false, false])
    const [models, setModels] = React.useState([])
    const [temp, setTemp] = React.useState(0)
    const [data, setData] = React.useState({"test":{"height":[900,880,700]}})
    const [shouldShowImage, setShouldShowImage] = React.useState([true, true, true, true, true, true, true, true, true, true]);
    const [shouldRunModel, setShouldRunModel] = React.useState([false, false, false, false, false, false, false, false, false, false]);



    // Screen size changing
         
    const [width, setWidth] = React.useState(window.innerWidth);

    function handleWindowSizeChange() {
        setWidth(window.innerWidth);
    }

    React.useEffect(() => {
        window.addEventListener('resize', handleWindowSizeChange);
        return () => {
            window.removeEventListener('resize', handleWindowSizeChange);
        }
    }, []);

    // const isTablet = width <= 1300;
    const nCols = width > 1800 ? 2 : (width > 1200 ? 2 : 1);

    // function getSize() {
    //     // return isMobile ? "100%" : "50%";
    //     return isMobile ? "100%" : (isTablet ? "75%" : "50%");
    // }


    function changeImageBool(index){
      console.log("changeImageBool");
      console.log(index);
      const newArr = shouldShowImage.slice();
      newArr[index] = !newArr[index];
      setShouldShowImage(newArr);
      console.log(newArr);
    }

    function changeRunModel(index){
      console.log("setShouldRunModel");
      console.log(index);
      const newArr = shouldRunModel.slice();
      newArr[index] = !newArr[index];
      setShouldRunModel(newArr);


      fetch("/set_infer", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model_index: index,
        }),
  
      }).then((res) =>
          res.json().then((jsondata) => {
  
          }).catch((err) => {
              console.log(err);
          })
      );
    }


    React.useEffect(() => {
      
      updateTemp();
      fetch("/models", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          a: 1
        }),
  
      }).then((res) =>
          res.json().then((jsondata) => {
              // Setting a data from api
              setModels(jsondata["models"]);
              console.log(jsondata["models"]);
  
          }).catch((err) => {
              console.log(err);
          })
      );
    }, [])

   
    function fetchData(){
      fetch("/data", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          a: 1
        }),
  
      }).then((res) =>
          res.json().then((jsondata) => {
            let jsdat = jsondata;

            let prevdat = data;

            let running_models = models.filter((e, i) => shouldRunModel[i]);
            console.log("running_models");
            console.log(running_models);
            for(let key in jsdat){
              console.log(key);
              if (key in running_models){
                continue;
              }
              if(key in prevdat){
                for(let key2 in jsdat[key]){
                  if(key2 in prevdat[key]){
                    prevdat[key][key2].push(jsdat[key][key2]);
                  } else{
                    prevdat[key][key2] = [jsdat[key][key2]];
                  }}
                }else{
                  prevdat[key] = [jsdat[key]];
              }
            }
            setData(prevdat);
            // setData(()=> data + {"changed": "new value"});
            // console.log("data HERE");
            // console.log(data);
            // console.log("jsdat");
            // console.log(jsdat);
          }).catch((err) => {
              console.log(err);
          })
      );
    }

    function updateTemp(){

      fetchData();
      setTemp((prevTemp)=>prevTemp+1);
      setTimeout(() => updateTemp(), 5000);
    }
  // React.useEffect(()=>{
  //   
  // }   
// )

    // useEffect(()=>{
    //   fetchData()
    // }, [temp])
    return (
      <>
      <Center margin = {8} height = "100%" minH = "100%">
      <Card maxW = "2500px" minW = "100%" minH = "100%" height = "100%" variant = "outline" borderRadius="lg">
        <CardHeader  bg = {col} >
          <Box width = "100%">
          <Flex  width = "100%">
              
              <DrawerModule checkedItems = {checkedItems} setCheckedItems = {setCheckedItems} models = {models}/>
              <Spacer />
              <Image src='/rwlogo.png' alt='Stenuld' width = "300px"/>
          </Flex>
          </Box>
         
          {/* <h2>{"Header" + temp + String(Object.entries(data["MOS IR"]))}</h2> */}
          {/* <h2>{"Data updated " + temp + " times"}</h2> */}
        </CardHeader>


        <Box position='relative' padding='10' bg = {col} >
          <Divider color ="white"/>
          <AbsoluteCenter bg = {col} px='4'>
             <Heading size="lg" fontFamily = "custom" textColor="white">The Tauro/Schauser Computer Vision Hub</Heading>
          </AbsoluteCenter>
        </Box>

        <CardBody>
        <Center>
        <SimpleGrid columns={Math.min(nCols, checkedItems.filter((e) => e).length)} spacing={2} margin = {6}>
          {checkedItems.map((item, index) => {
            if(item){
              return <SingleCard num={index} models = {models} data_for = {data} setShouldShowImage={changeImageBool} shouldShowImage={shouldShowImage[index]} setShouldRunModel = {changeRunModel} shouldRunModel={shouldRunModel[index]}/>
            }
          }
          )}
          </SimpleGrid>
        </Center>
          </CardBody>
        <CardFooter>
        {/* <Box position='absolute'  bottom='0' right='0' border ='solid #c6000e 1px' padding='2' textColor="#c6000e" margin = {4} borderRadius = "md" fontSize="md"> */}
          {/* <a href="mailto:sandeep.tauro@rockwool.com">Any questions? Click here to contact </a> */}
        {/* </Box> */}
        <Button variant='outline' colorScheme="ROCKWOOL" onClick={(event) => updateTemp()} minW = "150px" alignSelf="end">
          Any questions? Click here to contact
        </Button>
        </CardFooter>
      </Card>
      </Center>


    </>

    );
}



function SingleCard({num, models, data_for, setShouldShowImage, shouldShowImage, setShouldRunModel, shouldRunModel}){
  
  return ( 
    <Card maxW ='1000px' minW = "xl" borderRadius="lg">
      <CardHeader bg = {col}>
        {/* <Flex alignItems='center'> */}
       {/* <h1>{models[num]}</h1> */}
       <Center>
        <Heading size="lg" alignItems='center' textColor = "white"> {models[num]}</Heading>
        </Center>
        {/* TODO: Right allign X button */}
        {/* <Spacer /> */}
        {/* <IconButton aria-label="Close" icon={<CloseIcon />}/> */}
      {/* </Flex> */}
      
      </CardHeader>
      <CardBody align='center'>
        <Box bg = "white" min-width = "100px">
        {/* <Stack spacing={2} direction='column' width = "100%"> */}
          {/* <Image src={"/stream/"+num} alt="Segun Adebayo"/> */}
          <Flex minW ='100%' maxW="100%" justify = "space-between" direction = "column">
          <MyImage src={"/stream/"+num} sholdShow = {shouldShowImage}/>
          {/* <h1>{String(Object.keys(data[models[num]]))}</h1> */}
          {/* make container for the plot*/}
          {/* <Box minW = "100px" minH = "100px" bg = "black" > */}
          <PlotlyGraph data_for = {data_for} models = {models} num = {num}/>
          {/* </Box> */}

            
        </Flex>
          {/* </Stack> */}
        </Box>
      </CardBody>
        <Divider />
      <CardFooter>
        <HStack spacing={4}>
        <Button variant='outline' colorScheme={shouldShowImage ? 'ROCKWOOL' : "red"} onClick={(event) => setShouldShowImage(num)} minW = "150px">
          {shouldShowImage ? "Hide feed":"Feed hidden | click to show"}
        </Button>
        <Button variant='outline' colorScheme={shouldRunModel ? 'ROCKWOOL' : "red"} onClick={(event) => setShouldRunModel(num)} minW = "150px">
          {shouldRunModel ? "Pause model":"Model paused | click to re-enable"}
        </Button>
        </HStack>
          
      </CardFooter>
    </Card>


  );
}

function MyImage({src, sholdShow}){
  if(sholdShow){
    return <Image src={src} alt="Image loading"/>
  } else{
    return <></>
    // return <h1> No image </h1>
  }
}



function PlotlyGraph({data_for,  models, num}){
  if (!(models[num] in data_for)){
    return <h1> No data available </h1>
    }
  let df = Object.entries(data_for[models[num]]).filter((k, v) => {return Array.isArray(k[1]);});

  // console.log(df);
  const data = df.map(([key, value]) => {
      console.log(key);
      return {
        x: value.map((val, index) => {return index}).slice(-41,-1),
        y: value.slice(-41,-1),
        type: 'line',
        name: key
      }
  });
  // console.log(data);

  return <Box aspectRatio={2}><Plot  
            data={
              data
            }
            // layout={ {width: 400, height: 150, title: "", margin: {
            //   l: 50,
            //   r: 10,
            //   b: 0,
            //   t: 50,
            //   pad: 4
            // },} }
            layout = {{autosize: true, margin :{t:50, b:0, pad:4}, showlegend: true, }}
            useResizeHandler = {true}
            style = {{width: "100%", height:"100%"}}
          />
          </Box>
        }
export default App;
