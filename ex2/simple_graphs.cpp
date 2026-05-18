#include <Python.h>
#include <structmember.h>
#include <cstdint>

typedef struct {
    PyObject_HEAD
    uint16_t vertices;       
    uint16_t matrix[16];     
} AdjacencyMatrixObject;


static void clear_graph(AdjacencyMatrixObject *self) {
    self->vertices = 0;
    for (int i = 0; i < 16; i++) self->matrix[i] = 0;
}


static int AdjacencyMatrix_init(AdjacencyMatrixObject *self, PyObject *args, PyObject *kwds) {
    const char *text = "?"; 
    if (!PyArg_ParseTuple(args, "|s", &text)) return -1;

    clear_graph(self);

    // 1. Reading the number of vertices
    int n = text[0] - 63;
    if (n < 0) return 0; 
    if (n > 16) n = 16; 

    // Vertex bitmask (0 to n-1)
    for (int i = 0; i < n; i++) self->vertices |= (1 << i);

    // 2. Edge detection (Graph6 bitstream) https://users.cecs.anu.edu.au/~bdm/data/formats.txt
    int char_idx = 1;
    int bit_pos = -1; 
    uint8_t current_val = 0;

    for (int j = 1; j < n; j++) {
        for (int i = 0; i < j; i++) {
            if (bit_pos < 0) {
                if (text[char_idx] == '\0') break; 
                current_val = text[char_idx++] - 63;
                bit_pos = 5; 
            }

            if ((current_val >> bit_pos) & 1) {
                self->matrix[i] |= (1 << j);
                self->matrix[j] |= (1 << i);
            }
            bit_pos--;
        }
    }
    return 0;
}

static PyObject* AdjacencyMatrix_number_of_vertices(AdjacencyMatrixObject *self, PyObject *Py_UNUSED(ignored)) {
    int count = 0;
    for (int i = 0; i < 16; i++) {
        if ((self->vertices >> i) & 1) count++;
    }
    return PyLong_FromLong(count);
}

static PyObject* AdjacencyMatrix_vertices(AdjacencyMatrixObject *self, PyObject *Py_UNUSED(ignored)) {
    PyObject *result_set = PySet_New(NULL);
    for (int i = 0; i < 16; i++) {
        if ((self->vertices >> i) & 1) {
            PyObject *v = PyLong_FromLong(i);
            PySet_Add(result_set, v);
            Py_DECREF(v);
        }
    }
    return result_set;
}

static PyObject* AdjacencyMatrix_vertex_degree(AdjacencyMatrixObject *self, PyObject *args) {
    int v;
    // 1. We retrieve the vertex number
    if (!PyArg_ParseTuple(args, "i", &v)) return NULL;

    // 2. Wvalidation: if the vertex does not exist in the graph or the index is outside the range 0–15, the degree is 0
    if (v < 0 || v >= 16 || !((self->vertices >> v) & 1)) {
        return PyLong_FromLong(0);
    }

    // 3. We count the set bits in the mask of this vertex’s neighbours
    int degree = 0;
    uint16_t neighbors = self->matrix[v];
    
    for (int i = 0; i < 16; i++) {
        if ((neighbors >> i) & 1) {
            degree++;
        }
    }

    return PyLong_FromLong(degree);
}
static PyObject* AdjacencyMatrix_vertex_neighbors(AdjacencyMatrixObject *self, PyObject *args) {
    int v;
    if (!PyArg_ParseTuple(args, "i", &v)) return NULL;

    // 1. New, empty Python set
    PyObject *result_set = PySet_New(NULL);
    if (!result_set) return NULL;

    // 3. Whether the vertex exists and whether it lies within the range
    if (v >= 0 && v < 16 && ((self->vertices >> v) & 1)) {
        uint16_t neighbors_mask = self->matrix[v];
        
        // We are checking the bits in the neighbourhood mask
        for (int i = 0; i < 16; i++) {
            if ((neighbors_mask >> i) & 1) {
                // We create a number object and add it to the set
                PyObject *neighbor_val = PyLong_FromLong(i);
                PySet_Add(result_set, neighbor_val);
                Py_DECREF(neighbor_val);
            }
        }
    }
    
    return result_set;
}

static PyObject* AdjacencyMatrix_add_vertex(AdjacencyMatrixObject *self, PyObject *args) {
    int v;
    if (!PyArg_ParseTuple(args, "i", &v)) return NULL;

    if (v >= 0 && v < 16) {
        self->vertices |= (1 << v);
    }
    Py_RETURN_NONE;
}
static PyObject* AdjacencyMatrix_delete_vertex(AdjacencyMatrixObject *self, PyObject *args) {
    int v;
    if (!PyArg_ParseTuple(args, "i", &v)) return NULL;

    if (v >= 0 && v < 16) {
        // 1. Remove a vertex from the vertex mask
        self->vertices &= ~(1 << v);

        // 2. Clear the entire row v
        self->matrix[v] = 0;

        // 3. Clear column v in all other rows
        uint16_t mask = ~(1 << v);
        for (int i = 0; i < 16; i++) {
            self->matrix[i] &= mask;
        }
    }
    Py_RETURN_NONE;
}
static PyObject* AdjacencyMatrix_number_of_edges(AdjacencyMatrixObject *self, PyObject *Py_UNUSED(ignored)) {
    int total_bits = 0;
    for (int i = 0; i < 16; i++) {
        // We count the set bits in each row
        uint16_t row = self->matrix[i];
        while (row) {
            row &= (row - 1);
            total_bits++;
        }
    }
    // (u,v) and (v,u)
    return PyLong_FromLong(total_bits / 2);
}
static PyObject* AdjacencyMatrix_edges(AdjacencyMatrixObject *self, PyObject *Py_UNUSED(ignored)) {
    // 1. New Python set
    PyObject *result_set = PySet_New(NULL);
    if (!result_set) return NULL;

    // 2. We only examine the upper triangular part of the matrix (i < j)
    for (int i = 0; i < 16; i++) {
        if (!((self->vertices >> i) & 1)) continue;

        for (int j = i + 1; j < 16; j++) {
            if (!((self->vertices >> j) & 1)) continue;

            // Checking whether the edge exists
            if ((self->matrix[i] >> j) & 1) {
                // Create (i,j) tuple
                PyObject *u = PyLong_FromLong(i);
                PyObject *v = PyLong_FromLong(j);
                PyObject *tuple = PyTuple_Pack(2, u, v);

                PySet_Add(result_set, tuple);
                
                Py_DECREF(u);
                Py_DECREF(v);
                Py_DECREF(tuple);
            }
        }
    }
    return result_set;
}

static PyObject* AdjacencyMatrix_is_edge(AdjacencyMatrixObject *self, PyObject *args) {
    int u, v;
    if (!PyArg_ParseTuple(args, "ii", &u, &v)) return NULL;
    if (u < 0 || u >= 16 || v < 0 || v >= 16) Py_RETURN_FALSE;

    if ((self->matrix[u] >> v) & 1) Py_RETURN_TRUE;
    Py_RETURN_FALSE;
}
static PyObject* AdjacencyMatrix_add_edge(AdjacencyMatrixObject *self, PyObject *args) {
    int u, v;
    if (!PyArg_ParseTuple(args, "ii", &u, &v)) return NULL;

    if (u >= 0 && u < 16 && v >= 0 && v < 16) {
        self->matrix[u] |= (1 << v);
        self->matrix[v] |= (1 << u);
    }
    Py_RETURN_NONE;
}

static PyObject* AdjacencyMatrix_delete_edge(AdjacencyMatrixObject *self, PyObject *args) {
    int u, v;
    if (!PyArg_ParseTuple(args, "ii", &u, &v)) return NULL;

    if (u >= 0 && u < 16 && v >= 0 && v < 16) {
        self->matrix[u] &= ~(1 << v);
        self->matrix[v] &= ~(1 << u);
    }
    Py_RETURN_NONE;
}

static PyObject* AdjacencyMatrix_create_cycle(PyTypeObject *type, PyObject *args) {
    int n;
    if (!PyArg_ParseTuple(args, "i", &n)) return NULL;
    if (n < 0 || n > 16) {
        PyErr_SetString(PyExc_ValueError, "The number of vertices must be between 0 and 16!");
        return NULL;
    }

    // New instance AdjacencyMatrix
    AdjacencyMatrixObject *self = (AdjacencyMatrixObject *)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->vertices = 0;
        for (int i = 0; i < n; i++) {
            self->vertices |= (1 << i);
            self->matrix[i] = 0;
        }
        
        if (n > 2) {
            for (int i = 0; i < n; i++) {
                int next = (i + 1) % n;
                self->matrix[i] |= (1 << next);
                self->matrix[next] |= (1 << i);
            }
        } else if (n == 2) {
            self->matrix[0] |= (1 << 1);
            self->matrix[1] |= (1 << 0);
        }
    }
    return (PyObject *)self;
}


static PyMethodDef AdjacencyMatrix_methods[] = {
    {"number_of_vertices", (PyCFunction)AdjacencyMatrix_number_of_vertices, METH_NOARGS, NULL},
    {"vertices", (PyCFunction)AdjacencyMatrix_vertices, METH_NOARGS, NULL},
    {"number_of_edges", (PyCFunction)AdjacencyMatrix_number_of_edges, METH_NOARGS, NULL},
    {"edges", (PyCFunction)AdjacencyMatrix_edges, METH_NOARGS, NULL},
    {"is_edge", (PyCFunction)AdjacencyMatrix_is_edge, METH_VARARGS, NULL},
    {"add_edge", (PyCFunction)AdjacencyMatrix_add_edge, METH_VARARGS, NULL},
    {"delete_edge", (PyCFunction)AdjacencyMatrix_delete_edge, METH_VARARGS, NULL},
    {"add_vertex", (PyCFunction)AdjacencyMatrix_add_vertex, METH_VARARGS, NULL},
    {"delete_vertex", (PyCFunction)AdjacencyMatrix_delete_vertex, METH_VARARGS, NULL},
    {"vertex_degree", (PyCFunction)AdjacencyMatrix_vertex_degree, METH_VARARGS, NULL},
    {"vertex_neighbors", (PyCFunction)AdjacencyMatrix_vertex_neighbors, METH_VARARGS, NULL},
    {"create_cycle", (PyCFunction)AdjacencyMatrix_create_cycle, METH_VARARGS | METH_CLASS, NULL},
    {NULL, NULL, 0, NULL}
};

// https://docs.python.org/3/c-api/typeobj.html
static PyTypeObject AdjacencyMatrixType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    "simple_graphs.AdjacencyMatrix",             /* tp_name */
    sizeof(AdjacencyMatrixObject),               /* tp_basicsize */
    0,                                           /* tp_itemsize */
    0,                                           /* tp_dealloc */
    0,                                           /* tp_vectorcall_offset */
    0,                                           /* tp_getattr */
    0,                                           /* tp_setattr */
    0,                                           /* tp_as_async */
    0,                                           /* tp_repr */
    0,                                           /* tp_as_number */
    0,                                           /* tp_as_sequence */
    0,                                           /* tp_as_mapping */
    0,                                           /* tp_hash */
    0,                                           /* tp_call */
    0,                                           /* tp_str */
    0,                                           /* tp_getattro */
    0,                                           /* tp_setattro */
    0,                                           /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,    /* tp_flags */
    "Obiekt AdjacencyMatrix",                    /* tp_doc */
    0,                                           /* tp_traverse */
    0,                                           /* tp_clear */
    0,                                           /* tp_richcompare */
    0,                                           /* tp_weaklistoffset */
    0,                                           /* tp_iter */
    0,                                           /* tp_iternext */
    AdjacencyMatrix_methods,                     /* tp_methods */
    0,                                           /* tp_members */
    0,                                           /* tp_getset */
    0,                                           /* tp_base */
    0,                                           /* tp_dict */
    0,                                           /* tp_descr_get */
    0,                                           /* tp_descr_set */
    0,                                           /* tp_dictoffset */
    (initproc)AdjacencyMatrix_init,              /* tp_init */
    0,                                           /* tp_alloc */
    PyType_GenericNew,                           /* tp_new */
};

static PyModuleDef simple_graphs_module = {
    PyModuleDef_HEAD_INIT,
    "simple_graphs",                             /* m_name */
    "Module for handling simple graphs",           /* m_doc */
    -1,                                          /* m_size */
    NULL, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC PyInit_simple_graphs(void) {
    PyObject *m;
    if (PyType_Ready(&AdjacencyMatrixType) < 0) return NULL;
    m = PyModule_Create(&simple_graphs_module);
    if (m == NULL) return NULL;
    Py_INCREF(&AdjacencyMatrixType);
    if (PyModule_AddObject(m, "AdjacencyMatrix", (PyObject *)&AdjacencyMatrixType) < 0) {
        Py_DECREF(&AdjacencyMatrixType);
        Py_DECREF(m);
        return NULL;
    }
    return m;
}
