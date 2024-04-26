cmake_minimum_required(VERSION 3.4...3.18)
project(konoha)
set(PROJECT_VERSION "1.0.0")

set(CMAKE_CXX_STANDARD 20)

option(NEED_CONSOLE "Whether to build a console application." ON)
option(FREEZE_APPLICATION "Whether to freeze the python application." OFF)

if(${WIN32})
  set(PYTHON_EXECUTABLE
    ${CMAKE_CURRENT_SOURCE_DIR}/.venv/Scripts/python.exe
  )
else()
  set(PYTHON_EXECUTABLE
    ${CMAKE_CURRENT_SOURCE_DIR}/.venv/bin/python
  )
endif()

add_subdirectory(thirdparty)

set(SOURCES
  ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
)

if(FREEZE_APPLICATION)
  set(ENTRY_MODULE_NAME konoha)
  set(HIDDEN_IMPORTS "encodings.cp437,konoha.bridge.ast_editor,konoha.bridge.astvm_helper,konoha.bridge.file_editor,konoha.bridge.file_url_helper,konoha.bridge.interactive_interpreter,konoha.bridge.output_window_bridge,konoha.bridge.package_reloader,konoha.bridge.syntax_highlighter,konoha.bridge.astvms.expressions,konoha.bridge.astvms.root_nodes,konoha.bridge.astvms.statements")
  set(EXCLUDES "test,unittest,debugpy,black,_bz2,_decimal,_hashlib,_lzma,_socket,_ssl,_uuid,pyexpat,select,unicodedata")

  # Get frozen header file names
  execute_process(
    COMMAND ${PYTHON_EXECUTABLE} "-m" "qt_quick_python_tools.generate_frozen_modules" "--get-frozen-header-file-names" "${ENTRY_MODULE_NAME}"
    "--hidden-imports=${HIDDEN_IMPORTS}" "--excludes=${EXCLUDES}"
    OUTPUT_VARIABLE _frozen_headers
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE _resullt
  )

  if(${_resullt})
    message(FATAL_ERROR "Failed to get frozen header file names.")
  endif()

  add_custom_command(
    OUTPUT ${_frozen_headers}
    COMMAND
    ${CMAKE_CROSSCOMPILING_EMULATOR} ${PYTHON_EXECUTABLE} "-m" "qt_quick_python_tools.generate_frozen_modules" "--make-freeze"
    "${ENTRY_MODULE_NAME}" "--hidden-imports=${HIDDEN_IMPORTS}" "--excludes=${EXCLUDES}"
    WORKING_DIRECTORY
    ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT
    "Generating frozen module headers"
  )

  set(SOURCES
    ${SOURCES}
    ${_frozen_headers}
  )
endif()

# Add icons
include(${CMAKE_CURRENT_SOURCE_DIR}/cmake/add_icon_to_binary.cmake)
add_icon_to_binary(SOURCES ICONS
  ${CMAKE_CURRENT_SOURCE_DIR}/src/konoha/data/resource/icon.ico
  # Add MacOS icns file if you have one
  # ${CMAKE_CURRENT_SOURCE_DIR}/resource/icon.icns
)

add_executable(${PROJECT_NAME}
  ${SOURCES}
)

if(NEED_CONSOLE)
  target_compile_definitions(${PROJECT_NAME}
  PRIVATE
    NEED_CONSOLE
  )
endif()

if(FREEZE_APPLICATION)
  target_compile_definitions(${PROJECT_NAME}
    PRIVATE
    FREEZE_APPLICATION
  )
endif()

target_link_libraries(${PROJECT_NAME}
PRIVATE
  cpython::libpython
)

if(${WIN32})
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_RUNTIME_DLLS:${PROJECT_NAME}> $<TARGET_FILE_DIR:${PROJECT_NAME}>
    COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:cpython::libpython3> $<TARGET_FILE_DIR:${PROJECT_NAME}>
    COMMAND_EXPAND_LISTS
  )
  set(PYTHON_VERSIONS_LIST 3 311 312)
  set(PYTHON_ADDITIONAL_LINK_FLAGS "")
  foreach(VER ${PYTHON_VERSIONS_LIST})
    set(PYTHON_ADDITIONAL_LINK_FLAGS
        "${PYTHON_ADDITIONAL_LINK_FLAGS} /NODEFAULTLIB:\"python${VER}_d.lib\"")
    set(PYTHON_ADDITIONAL_LINK_FLAGS
        "${PYTHON_ADDITIONAL_LINK_FLAGS} /NODEFAULTLIB:\"python${VER}.lib\"")
  endforeach()
  set_target_properties(${PROJECT_NAME} PROPERTIES LINK_FLAGS "${PYTHON_ADDITIONAL_LINK_FLAGS}")
  if(NOT NEED_CONSOLE)
    set_target_properties(${PROJECT_NAME} PROPERTIES WIN32_EXECUTABLE 1)
  endif()
  if(FREEZE_APPLICATION)
    add_custom_command(TARGET ${PROJECT_NAME} POST_BUILD
      COMMAND ${PYTHON_EXECUTABLE} "-m" "qt_quick_python_tools.code_sign" $<TARGET_FILE:${PROJECT_NAME}>
      COMMAND ${PYTHON_EXECUTABLE} "-m" "qt_quick_python_tools.assemble_application"
      "${ENTRY_MODULE_NAME}" "--hidden-imports=${HIDDEN_IMPORTS}" "--excludes=${EXCLUDES}" "--binaries=$<TARGET_FILE:${PROJECT_NAME}>,$<TARGET_FILE:cpython::libpython3>"
      "--pyside6-modules=PySide6.QtCore,PySide6.QtGui,PySide6.QtQuick,PySide6.QtQml"
      "--qml-directory=${CMAKE_CURRENT_SOURCE_DIR}/src/konoha/data/view"
      "--qt-quick-control-styles=Material"
      "--dont-ignore-platform-dynload"
      COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:cpython::libpython3> ${CMAKE_CURRENT_SOURCE_DIR}/deployment
      WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    )
  endif()
endif()
