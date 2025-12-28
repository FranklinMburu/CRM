<script setup>
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { crmService } from '../services/api'

const route = useRoute()
const tasks = ref([])
const deals = ref([])
const contacts = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const editedIndex = ref(-1)
const editedItem = ref({
  title: '',
  description: '',
  status: 'pending',
  priority: 'medium',
  due_date: '',
  deal: null,
  assigned_to: null
})

const defaultItem = {
  title: '',
  description: '',
  status: 'pending',
  priority: 'medium',
  due_date: '',
  deal: null,
  assigned_to: null
}

const statusOptions = [
  { title: 'Pending', value: 'pending' },
  { title: 'In Progress', value: 'in_progress' },
  { title: 'Completed', value: 'completed' }
]

const priorityOptions = [
  { title: 'Low', value: 'low' },
  { title: 'Medium', value: 'medium' },
  { title: 'High', value: 'high' }
]

const headers = [
  { title: 'Task', key: 'title', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Priority', key: 'priority', sortable: true },
  { title: 'Deal', key: 'deal_title', sortable: false },
  { title: 'Due Date', key: 'due_date', sortable: true },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

const filteredTasks = computed(() => {
  if (!search.value) return tasks.value
  const searchLower = search.value.toLowerCase()
  return tasks.value.filter(task =>
    task.title && task.title.toLowerCase().includes(searchLower) ||
    task.description && task.description.toLowerCase().includes(searchLower) ||
    task.status && task.status.toLowerCase().includes(searchLower) ||
    task.deal_title && task.deal_title.toLowerCase().includes(searchLower)
  )
})

onMounted(async () => {
  await Promise.all([loadTasks(), loadDeals(), loadContacts()])
})

onActivated(async () => {
  await Promise.all([loadTasks(), loadDeals(), loadContacts()])
})

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await crmService.getTasks()
    tasks.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

const loadDeals = async () => {
  try {
    const response = await crmService.getDeals()
    deals.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load deals:', error)
  }
}

const loadContacts = async () => {
  try {
    const response = await crmService.getContacts()
    contacts.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load contacts:', error)
  }
}

const getStatusColor = (status) => {
  const colors = {
    pending: 'orange',
    in_progress: 'blue',
    completed: 'green'
  }
  return colors[status] || 'grey'
}

const getPriorityColor = (priority) => {
  const colors = {
    low: 'blue',
    medium: 'orange',
    high: 'red'
  }
  return colors[priority] || 'grey'
}

const formatDate = (date) => {
  if (!date) return 'No date'
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  }).format(new Date(date))
}

const isOverdue = (dueDate, status) => {
  if (!dueDate || status === 'completed') return false
  return new Date(dueDate) < new Date()
}

const editItem = (item) => {
  editedIndex.value = tasks.value.indexOf(item)
  editedItem.value = Object.assign({}, item)
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this task?')) {
    try {
      await crmService.deleteTask(item.id)
      await loadTasks()
    } catch (error) {
      console.error('Failed to delete task:', error)
    }
  }
}

const close = () => {
  dialog.value = false
  setTimeout(() => {
    editedItem.value = Object.assign({}, defaultItem)
    editedIndex.value = -1
  }, 300)
}

const save = async () => {
  try {
    if (editedIndex.value > -1) {
      await crmService.updateTask(editedItem.value.id, editedItem.value)
    } else {
      await crmService.createTask(editedItem.value)
    }
    await loadTasks()
    close()
  } catch (error) {
    console.error('Failed to save task:', error)
  }
}

const getTaskIcon = (status) => {
  const icons = {
    pending: 'mdi-clock-outline',
    in_progress: 'mdi-progress-clock',
    completed: 'mdi-check-circle'
  }
  return icons[status] || 'mdi-checkbox-marked-circle-outline'
}

const getTaskColor = (index) => {
  const colors = ['primary', 'secondary', 'success', 'info', 'warning', 'purple', 'pink', 'indigo', 'teal', 'orange']
  return colors[index % colors.length]
}
</script>

<template>
  <v-container fluid class="pa-6">
    <v-row>
      <v-col cols="12">
        <div class="d-flex justify-space-between align-center mb-6 flex-wrap gap-3">
          <div>
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Tasks</h1>
            <p class="text-h6 text-grey-darken-1">Manage your to-do list</p>
          </div>
          <v-btn color="primary" size="large" prepend-icon="mdi-plus" @click="dialog = true" elevation="2">
            Add Task
          </v-btn>
        </div>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <v-card elevation="2" class="mb-4">
          <v-card-text class="pa-4">
            <div class="d-flex align-center gap-3 flex-wrap">
              <v-text-field
                v-model="search"
                prepend-inner-icon="mdi-magnify"
                label="Search tasks..."
                variant="outlined"
                density="compact"
                hide-details
                clearable
                class="flex-grow-1"
                style="max-width: 400px;"
              ></v-text-field>
              <v-spacer></v-spacer>
              <v-btn-toggle v-model="viewMode" mandatory variant="outlined" divided density="compact">
                <v-btn value="card" size="small"><v-icon>mdi-view-grid</v-icon></v-btn>
                <v-btn value="table" size="small"><v-icon>mdi-view-list</v-icon></v-btn>
              </v-btn-toggle>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-if="loading">
      <v-col cols="12" class="text-center py-12">
        <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
      </v-col>
    </v-row>

    <v-row v-else-if="viewMode === 'card'">
      <v-col v-for="(task, index) in filteredTasks" :key="task.id" cols="12" sm="6" md="4" lg="3">
        <v-card elevation="3" class="task-card h-100" hover :class="{ 'overdue-card': isOverdue(task.due_date, task.status) }">
          <v-card-text class="pa-4">
            <div class="d-flex align-center mb-3">
              <v-avatar :color="getTaskColor(index)" size="48" class="mr-3">
                <v-icon :icon="getTaskIcon(task.status)" color="white" size="28"></v-icon>
              </v-avatar>
              <div class="flex-grow-1">
                <div class="d-flex align-center gap-1 mb-1">
                  <v-chip :color="getPriorityColor(task.priority)" size="x-small" variant="flat" class="text-capitalize font-weight-bold">
                    {{ task.priority }}
                  </v-chip>
                  <v-chip v-if="isOverdue(task.due_date, task.status)" color="error" size="x-small" variant="flat" prepend-icon="mdi-alert">
                    Overdue
                  </v-chip>
                </div>
              </div>
            </div>

            <h3 class="text-h6 font-weight-bold mb-2">{{ task.title }}</h3>
            <p v-if="task.description" class="text-caption text-grey-darken-1 mb-3 task-description">{{ task.description }}</p>

            <v-divider class="my-3"></v-divider>

            <div class="task-details">
              <div class="d-flex align-center mb-2">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-chart-timeline-variant</v-icon>
                <v-chip :color="getStatusColor(task.status)" size="x-small" variant="tonal" class="text-capitalize">
                  {{ task.status.replace('_', ' ') }}
                </v-chip>
              </div>

              <div class="d-flex align-center mb-2" v-if="task.deal_title">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-handshake</v-icon>
                <span class="text-caption font-weight-medium">{{ task.deal_title }}</span>
              </div>

              <div class="d-flex align-center" v-if="task.due_date">
                <v-icon size="small" class="mr-2" :color="isOverdue(task.due_date, task.status) ? 'error' : 'grey-darken-1'">mdi-calendar</v-icon>
                <span class="text-caption" :class="{ 'text-error font-weight-bold': isOverdue(task.due_date, task.status) }">
                  {{ formatDate(task.due_date) }}
                </span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="pa-3 pt-0">
            <v-btn size="small" variant="text" color="primary" prepend-icon="mdi-pencil" @click="editItem(task)">
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn size="small" variant="text" color="error" icon="mdi-delete" @click="deleteItem(task)"></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="filteredTasks.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-clipboard-check-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No tasks found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first task' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-plus">Add Task</v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table :headers="headers" :items="filteredTasks" :loading="loading" items-per-page="15">
            <template v-slot:item.title="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getTaskColor(index)" size="36" class="mr-3">
                  <v-icon :icon="getTaskIcon(item.status)" color="white" size="20"></v-icon>
                </v-avatar>
                <div>
                  <div class="font-weight-medium">{{ item.title }}</div>
                  <div v-if="item.description" class="text-caption text-grey text-truncate" style="max-width: 300px;">
                    {{ item.description }}
                  </div>
                </div>
              </div>
            </template>
            <template v-slot:item.status="{ item }">
              <v-chip :color="getStatusColor(item.status)" size="small" variant="flat" class="text-capitalize font-weight-bold">
                {{ item.status.replace('_', ' ') }}
              </v-chip>
            </template>
            <template v-slot:item.priority="{ item }">
              <v-chip :color="getPriorityColor(item.priority)" size="small" variant="tonal" class="text-capitalize font-weight-bold">
                {{ item.priority }}
              </v-chip>
            </template>
            <template v-slot:item.deal_title="{ item }">
              <v-chip v-if="item.deal_title" size="small" variant="tonal" prepend-icon="mdi-handshake">
                {{ item.deal_title }}
              </v-chip>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.due_date="{ item }">
              <div v-if="item.due_date" class="d-flex align-center gap-1">
                <span :class="{ 'text-error font-weight-bold': isOverdue(item.due_date, item.status) }">
                  {{ formatDate(item.due_date) }}
                </span>
                <v-chip v-if="isOverdue(item.due_date, item.status)" color="error" size="x-small" variant="flat">
                  Overdue
                </v-chip>
              </div>
              <span v-else class="text-grey">-</span>
            </template>
            <template v-slot:item.actions="{ item }">
              <v-icon size="small" class="mr-2" @click="editItem(item)" color="primary">mdi-pencil</v-icon>
              <v-icon size="small" @click="deleteItem(item)" color="error">mdi-delete</v-icon>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="dialog" max-width="700px" persistent>
      <v-card>
        <v-card-title class="pa-4 bg-grey-lighten-4">
          <div class="d-flex align-center">
            <v-icon class="mr-2" color="primary">{{ editedIndex === -1 ? 'mdi-clipboard-plus' : 'mdi-clipboard-edit' }}</v-icon>
            <span class="text-h6 font-weight-bold">{{ editedIndex === -1 ? 'New Task' : 'Edit Task' }}</span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-container>
            <v-row>
              <v-col cols="12">
                <v-text-field
                  v-model="editedItem.title"
                  label="Task Title *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text"
                  required
                ></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-textarea
                  v-model="editedItem.description"
                  label="Description"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-text-box"
                  rows="3"
                ></v-textarea>
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="editedItem.status"
                  :items="statusOptions"
                  label="Status *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-chart-timeline-variant"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" sm="4">
                <v-select
                  v-model="editedItem.priority"
                  :items="priorityOptions"
                  label="Priority *"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-flag"
                  required
                ></v-select>
              </v-col>
              <v-col cols="12" sm="4">
                <v-text-field
                  v-model="editedItem.due_date"
                  label="Due Date"
                  type="date"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-calendar"
                ></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.deal"
                  :items="deals"
                  item-title="title"
                  item-value="id"
                  label="Related Deal"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-handshake"
                  clearable
                  hint="Optional: Link this task to a deal"
                  persistent-hint
                ></v-select>
              </v-col>
              <v-col cols="12" sm="6">
                <v-select
                  v-model="editedItem.assigned_to"
                  :items="contacts"
                  item-title="email"
                  item-value="id"
                  label="Assign To"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-account"
                  clearable
                  hint="Optional: Assign this task to a contact"
                  persistent-hint
                >
                  <template v-slot:item="{ props, item }">
                    <v-list-item v-bind="props" :title="`${item.raw.first_name} ${item.raw.last_name}`" :subtitle="item.raw.email"></v-list-item>
                  </template>
                  <template v-slot:selection="{ item }">
                    {{ item.raw.first_name }} {{ item.raw.last_name }}
                  </template>
                </v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="close" size="large">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="save" size="large" prepend-icon="mdi-content-save">Save Task</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.task-card {
  transition: all 0.3s ease;
  border-left: 4px solid transparent;
}

.task-card:hover {
  transform: translateY(-4px);
  border-left-color: rgb(var(--v-theme-primary));
}

.overdue-card {
  border-left-color: rgb(var(--v-theme-error)) !important;
}

.task-details {
  min-height: 80px;
}

.task-description {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
  max-height: 2.8em;
}

.text-navy {
  color: #1a237e;
}
</style>
