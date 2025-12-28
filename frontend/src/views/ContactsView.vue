<script setup>
import { ref, onMounted, computed, onActivated } from 'vue'
import { useRoute } from 'vue-router'
import { crmService } from '../services/api'

const route = useRoute()
const contacts = ref([])
const companies = ref([])
const loading = ref(true)
const dialog = ref(false)
const viewMode = ref('card')
const search = ref('')
const editedIndex = ref(-1)
const editedItem = ref({
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  position: '',
  company: null
})

const defaultItem = {
  first_name: '',
  last_name: '',
  email: '',
  phone: '',
  position: '',
  company: null
}

const headers = [
  { title: 'Name', key: 'full_name', sortable: true },
  { title: 'Email', key: 'email', sortable: true },
  { title: 'Phone', key: 'phone', sortable: false },
  { title: 'Company', key: 'company_name', sortable: true },
  { title: 'Position', key: 'position', sortable: false },
  { title: 'Actions', key: 'actions', sortable: false, align: 'end' }
]

const filteredContacts = computed(() => {
  if (!search.value) return contacts.value
  const searchLower = search.value.toLowerCase()
  return contacts.value.filter(contact =>
    contact.first_name && contact.first_name.toLowerCase().includes(searchLower) ||
    contact.last_name && contact.last_name.toLowerCase().includes(searchLower) ||
    contact.email && contact.email.toLowerCase().includes(searchLower) ||
    contact.company_name && contact.company_name.toLowerCase().includes(searchLower)
  )
})

onMounted(async () => {
  await Promise.all([loadContacts(), loadCompanies()])
})

onActivated(async () => {
  await Promise.all([loadContacts(), loadCompanies()])
})

const loadContacts = async () => {
  loading.value = true
  try {
    const response = await crmService.getContacts()
    contacts.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load contacts:', error)
  } finally {
    loading.value = false
  }
}

const loadCompanies = async () => {
  try {
    const response = await crmService.getCompanies()
    companies.value = response.results || response || []
  } catch (error) {
    console.error('Failed to load companies:', error)
  }
}

const editItem = (item) => {
  editedIndex.value = contacts.value.indexOf(item)
  editedItem.value = Object.assign({}, item)
  dialog.value = true
}

const deleteItem = async (item) => {
  if (confirm('Are you sure you want to delete this contact?')) {
    try {
      await crmService.deleteContact(item.id)
      await loadContacts()
    } catch (error) {
      console.error('Failed to delete contact:', error)
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
      await crmService.updateContact(editedItem.value.id, editedItem.value)
    } else {
      await crmService.createContact(editedItem.value)
    }
    await loadContacts()
    close()
  } catch (error) {
    console.error('Failed to save contact:', error)
  }
}

const getInitials = (firstName, lastName) => {
  const first = firstName && firstName.length > 0 ? firstName[0] : ''
  const last = lastName && lastName.length > 0 ? lastName[0] : ''
  return (first + last).toUpperCase()
}

const getAvatarColor = (index) => {
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
            <h1 class="text-h3 font-weight-bold text-navy mb-2">Contacts</h1>
            <p class="text-h6 text-grey-darken-1">Manage your professional network</p>
          </div>
          <v-btn color="primary" size="large" prepend-icon="mdi-plus" @click="dialog = true" elevation="2">
            Add Contact
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
                label="Search contacts..."
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
      <v-col v-for="(contact, index) in filteredContacts" :key="contact.id" cols="12" sm="6" md="4" lg="3">
        <v-card elevation="3" class="contact-card h-100" hover>
          <v-card-text class="pa-4 text-center">
            <v-avatar :color="getAvatarColor(index)" size="64" class="mb-3">
              <span class="text-h5 font-weight-bold text-white">
                {{ getInitials(contact.first_name, contact.last_name) }}
              </span>
            </v-avatar>
            <h3 class="text-h6 font-weight-bold mb-1">{{ contact.first_name }} {{ contact.last_name }}</h3>
            <p class="text-caption text-grey mb-3">{{ contact.position || 'No position' }}</p>
            
            <v-divider class="my-3"></v-divider>
            
            <div class="contact-details text-left">
              <div class="d-flex align-center mb-2" v-if="contact.company_name">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-office-building</v-icon>
                <span class="text-caption font-weight-medium">{{ contact.company_name }}</span>
              </div>
              <div class="d-flex align-center mb-2" v-if="contact.email">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-email</v-icon>
                <span class="text-caption text-truncate">{{ contact.email }}</span>
              </div>
              <div class="d-flex align-center" v-if="contact.phone">
                <v-icon size="small" class="mr-2" color="grey-darken-1">mdi-phone</v-icon>
                <span class="text-caption">{{ contact.phone }}</span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions class="pa-3 pt-0">
            <v-btn size="small" variant="text" color="primary" prepend-icon="mdi-pencil" @click="editItem(contact)">
              Edit
            </v-btn>
            <v-spacer></v-spacer>
            <v-btn size="small" variant="text" color="error" icon="mdi-delete" @click="deleteItem(contact)"></v-btn>
          </v-card-actions>
        </v-card>
      </v-col>

      <v-col v-if="filteredContacts.length === 0" cols="12">
        <v-card elevation="2" class="pa-12">
          <div class="text-center">
            <v-icon size="64" color="grey-lighten-1" class="mb-4">mdi-account-outline</v-icon>
            <h3 class="text-h5 mb-2 text-grey-darken-1">No contacts found</h3>
            <p class="text-body-2 text-grey mb-4">
              {{ search ? 'Try adjusting your search' : 'Get started by adding your first contact' }}
            </p>
            <v-btn v-if="!search" color="primary" @click="dialog = true" prepend-icon="mdi-plus">Add Contact</v-btn>
          </div>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col cols="12">
        <v-card elevation="3">
          <v-data-table :headers="headers" :items="filteredContacts" :loading="loading" items-per-page="15">
            <template v-slot:item.full_name="{ item, index }">
              <div class="d-flex align-center py-2">
                <v-avatar :color="getAvatarColor(index)" size="36" class="mr-3">
                  <span class="text-caption font-weight-bold text-white">
                    {{ getInitials(item.first_name, item.last_name) }}
                  </span>
                </v-avatar>
                <span class="font-weight-medium">{{ item.first_name }} {{ item.last_name }}</span>
              </div>
            </template>
            <template v-slot:item.company_name="{ item }">
              <v-chip v-if="item.company_name" size="small" variant="tonal" prepend-icon="mdi-office-building">
                {{ item.company_name }}
              </v-chip>
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
            <v-icon class="mr-2" color="primary">{{ editedIndex === -1 ? 'mdi-account-plus' : 'mdi-account-edit' }}</v-icon>
            <span class="text-h6 font-weight-bold">{{ editedIndex === -1 ? 'New Contact' : 'Edit Contact' }}</span>
          </div>
        </v-card-title>
        <v-divider></v-divider>
        <v-card-text class="pa-6">
          <v-container>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editedItem.first_name" label="First Name *" variant="outlined" color="primary" prepend-inner-icon="mdi-account" required></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editedItem.last_name" label="Last Name *" variant="outlined" color="primary" prepend-inner-icon="mdi-account" required></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-text-field v-model="editedItem.email" label="Email *" type="email" variant="outlined" color="primary" prepend-inner-icon="mdi-email" required></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editedItem.phone" label="Phone" variant="outlined" color="primary" prepend-inner-icon="mdi-phone"></v-text-field>
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field v-model="editedItem.position" label="Position" variant="outlined" color="primary" prepend-inner-icon="mdi-briefcase"></v-text-field>
              </v-col>
              <v-col cols="12">
                <v-select
                  v-model="editedItem.company"
                  :items="companies"
                  item-title="name"
                  item-value="id"
                  label="Company"
                  variant="outlined"
                  color="primary"
                  prepend-inner-icon="mdi-office-building"
                  clearable
                  hint="Optional: Select a company to link this contact"
                  persistent-hint
                ></v-select>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn color="grey" variant="text" @click="close" size="large">Cancel</v-btn>
          <v-btn color="primary" variant="flat" @click="save" size="large" prepend-icon="mdi-content-save">Save Contact</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.contact-card {
  transition: all 0.3s ease;
  border-top: 4px solid transparent;
}

.contact-card:hover {
  transform: translateY(-4px);
  border-top-color: rgb(var(--v-theme-primary));
}

.contact-details {
  min-height: 72px;
}

.text-navy {
  color: #1a237e;
}
</style>
