# **Project Persistence & File Specification**

## **Overview**

EpiGimp utilizes a custom, binary-based file format (.epigimp) to ensure the non-destructive persistence of projects. Unlike standard image formats (PNG/JPG) that flatten visual data, the EpiGimp format preserves:

* The complete **Layer Stack** (visibility, opacity, blending modes).  
* **Raw Pixel Data** (NumPy arrays).  
* **Canvas Metadata** (dimensions, EXIF, IPTC).

This document details the serialization workflow and the binary structure of the file format.

## **Architecture & Data Flow**

The saving process converts the runtime state (Canva object) into a serialized binary stream via the FileSaver utility.

1. **State Aggregation (save\_project)**: The Canvas iterates through its layer stack, extracting mutable properties (opacity, visibility) and the raw pixel buffers.  
2. **Metadata Serialization**: Global project metadata and canvas dimensions are bundled into a dictionary.  
3. **Binary Packing (\_save\_native\_format)**: The system uses Python's struct module to pack integers and json for variable-length metadata strings into a specific byte layout.

## **The .epigimp File Format Specification**

The file format is designed as a sequential binary stream featuring a fixed header followed by variable-length data blocks. All integers are unsigned and encoded in **Little-Endian** (\<I) byte order.

### **1\. File Header**

The header identifies the file type and version to ensure compatibility.

### **2\. Global Metadata Block**

Immediately following the header is the global metadata (canvas size, author info, etc.).

### **3\. Layer Stack Block**

The remainder of the file contains the layer data.

## **API Reference**

### **Canva.save\_project**

**Description:**  
Orchestrates the serialization of the current project state. It acts as the bridge between the runtime application state and the file I/O layer.  
**Parameters:**

* filename (*str*): The absolute system path where the .epigimp file will be written.

**Workflow:**

1. Updates the modification\_time in the metadata.  
2. Constructs a layers\_data list, decoupling the Layer objects into serializable dictionaries containing:  
   * name, visible, opacity, blend\_mode, position, data (pixels).  
3. Delegates the actual writing process to FileSaver.save\_project.

### **FileSaver.\_save\_native\_format**

**Description:**  
Implements the low-level binary writing logic. This method is responsible for opening the file handle and ensuring the byte alignment matches the specification.  
**Parameters:**

* layers (*List\[Dict\]*): A list of dictionaries representing the visual layers.  
* metadata (*Dict*, optional): The canvas-level metadata.

**Implementation Details:**

* **Magic Bytes**: Writes b'EPIGIMP\\x00' to the first 8 bytes.  
* **Struct Packing**: Uses struct.pack('\<I', value) to write 4-byte unsigned integers for versions and string lengths.  
* **JSON Encoding**: Metadata is serialized to a JSON string and encoded to utf-8 before writing. This allows for flexible metadata fields without changing the binary schema.  
* **Iterative Writing**: Loops through the layers list and delegates individual layer serialization to \_write\_layer.

**Security Note:**  
The format uses standard JSON and specific struct packing. When loading files (FileLoader), the magic bytes must be verified to prevent processing invalid or malicious files.
