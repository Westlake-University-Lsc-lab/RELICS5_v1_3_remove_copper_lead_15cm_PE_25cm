cmake_minimum_required(VERSION 3.16)
project(BambooMC VERSION 2.0 LANGUAGES CXX)

# check for cxx compiler flag
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(CMAKE_MODULE_PATH ${CMAKE_CURRENT_SOURCE_DIR}/cmake)

# geant4
find_package(Geant4 REQUIRED ui_all vis_all)
include(${Geant4_USE_FILE})
include_directories(${Geant4_INCLUDE_DIRS})

# root
find_package(ROOT REQUIRED)

# Qt6
find_package(Qt6 REQUIRED COMPONENTS Core)
message("Found Qt6Core version ${Qt6Core_VERSION}")
include_directories(${Qt6Core_INCLUDE_DIRS})
set(QTLIB Qt6::Core)

# find yaml-cpp
find_package(yaml-cpp 0.6 NO_MODULE)
if(yaml-cpp_FOUND)
  message("found yaml-cpp version ${yaml-cpp_VERSION}")
  include_directories(${YAML_CPP_INCLUDE_DIR})
endif()


# set include directories
include_directories(${PROJECT_SOURCE_DIR}/include ${CMAKE_CURRENT_BINARY_DIR})

find_package(Git)
if(GIT_FOUND AND EXISTS "${CMAKE_SOURCE_DIR}/.git")
#    INCLUDE(GetGitRevisionDescription)
    EXECUTE_PROCESS(COMMAND ${GIT_EXECUTABLE} describe --tags --dirty --always OUTPUT_VARIABLE SHORT_SHA OUTPUT_STRIP_TRAILING_WHITESPACE)

    SET(REVISION ${SHORT_SHA} CACHE STRING "git short sha" FORCE)

    # only use the plugin to tie the configure state to the sha to force rebuilds
    # of files that depend on version.hh
    include(GetGitRevisionDescription)
    get_git_head_revision(REFSPEC COMMITHASH)

else()
    message(WARNING "Git not found, cannot set version info")

    SET(REVISION "unknown")
endif()
  
# generate version.h
include_directories(${CMAKE_BINARY_DIR})
configure_file("${CMAKE_SOURCE_DIR}/include/version.hh.in" "${CMAKE_BINARY_DIR}/version.hh" @ONLY)

# enable detector sets
set(ENABLE_DETECTOR_SETS "relics" CACHE STRING "The detector sets to be enabled")
if(ENABLE_DETECTOR_SETS)
  string(REPLACE "," ";" DETECTOR_SET_LIST ${ENABLE_DETECTOR_SETS})
  foreach(DETECTOR_SET ${DETECTOR_SET_LIST})
    include(${PROJECT_SOURCE_DIR}/user/detectors/${DETECTOR_SET}/sources.cmake)
    include_directories(${PROJECT_SOURCE_DIR}/user/detectors/${DETECTOR_SET})
  endforeach(DETECTOR_SET)
  add_library(UserDetector ${Detector})
  target_link_libraries(UserDetector ${Geant4_LIBRARIES})
endif(ENABLE_DETECTOR_SETS)

# enable user mc
set(ENABLE_USER_MC "pandax,relics" CACHE STRING "The User MC to be enabled")
if(ENABLE_USER_MC)
  string(REPLACE "," ";" USER_MC_LIST ${ENABLE_USER_MC})
  foreach(USER_MC ${USER_MC_LIST})
    include(${PROJECT_SOURCE_DIR}/user/mc/${USER_MC}/sources.cmake)
    include_directories(${PROJECT_SOURCE_DIR}/user/mc/${USER_MC})
  endforeach(USER_MC)
  add_library(UserMC ${UserMC})
  target_include_directories(UserMC PRIVATE ${ROOT_INCLUDE_DIRS})
  target_link_libraries(UserMC ${Geant4_LIBRARIES} ${ROOT_LIBRARIES})
endif(ENABLE_USER_MC)

add_library(BambooCore src/BambooControl.cc src/BambooUtils.cc src/BambooDetectorConstruction.cc)
target_link_libraries(BambooCore ${QTLIB} ${Geant4_LIBRARIES})
if(yaml-cpp_FOUND)
  target_compile_definitions(BambooCore PUBLIC WITH_YAML_CPP)
  target_link_libraries(BambooCore ${YAML_CPP_LIBRARIES})
endif()

set(PandaXAnalysis src/PandaXEnergyDepositionHit.cc src/PandaXSurfaceFluxHit.cc src/PandaXSensitiveDetector.cc src/PandaXTrackingAction.cc src/PandaXDataManager.cc src/PandaXRunAction.cc src/PandaXEventAction.cc src/PandaXStackingAction.cc src/PandaXSteppingAction.cc src/PandaXAnalysis.cc)

add_library(PandaXMC src/PandaXPhysics.cc src/SimpleGPSGenerator.cc src/HEPEvtLoader.cc src/GdmlLoader.cc ${PandaXAnalysis})
target_include_directories(PandaXMC PRIVATE ${ROOT_INCLUDE_DIRS})
target_link_libraries(PandaXMC ${Geant4_LIBRARIES} ${ROOT_LIBRARIES})

add_executable(BambooMC BambooMC.cc)
target_link_libraries(BambooMC ${Geant4_LIBRARIES} BambooCore)
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  target_link_libraries(BambooMC "-Wl,--whole-archive" PandaXMC "-Wl,--no-whole-archive")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  target_link_libraries(BambooMC "-Wl,-all_load" PandaXMC)
endif()

if(ENABLE_DETECTOR_SETS)
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  target_link_libraries(BambooMC "-Wl,--whole-archive" UserDetector "-Wl,--no-whole-archive")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  target_link_libraries(BambooMC "-Wl,-all_load" UserDetector)
endif()
endif(ENABLE_DETECTOR_SETS)

if(ENABLE_USER_MC)
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
  target_link_libraries(BambooMC "-Wl,--whole-archive" UserMC "-Wl,--no-whole-archive")
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  target_link_libraries(BambooMC "-Wl,-all_load" UserMC)
endif()
endif(ENABLE_USER_MC)

install(TARGETS BambooMC RUNTIME DESTINATION bin)
install(DIRECTORY config/ DESTINATION share/bamboo-mc/config)
install(DIRECTORY macro/ DESTINATION share/bamboo-mc/macro)
install(DIRECTORY data/ DESTINATION share/bamboo-mc/data)
