<template>
<div class="admin-page">
  <div class="action-menu">
    <div class="float-right">
      <b-form @submit="onImport">
        <b-form-group>
          <b-form-file
            v-model="projectsFile"
            :state="Boolean(projectsFile)"
            placeholder="Choose a file or drop it here..."
            drop-placeholder="Drop file here..."
          ></b-form-file>
          <b-button type="submit" variant="primary">Import</b-button>
        </b-form-group>
      </b-form>
    </div>
    <b-button href="/admin/project/add" variant="primary">Create new project</b-button>
    <b-spinner v-if="applying" variant="success" label="Applying..."></b-spinner>
  </div>
  <div class="projects-table position-relative">
    <b-table v-if="projects.length" sort-by="uid" striped hover :items="projects" :fields="fields">
      <template v-slot:cell(name)="row">
        {{ row.value }}
      </template>
      <template v-slot:cell(active)="row">
        <b-badge :variant="row.value?'success':'warning'">{{row.value?'active':'inactive'}}</b-badge>
      </template>
      <template v-slot:cell(actions)="row">
        <b-button variant="primary" size="sm" :href="'/admin/project/'+row.item.uid">Edit</b-button>
        <b-button variant="danger" size="sm" @click="onDelete(row.item.uid)">Delete</b-button>
        <b-button v-if="row.item.active == false" variant="success" size="sm" @click="onActivate(row.item.uid)">Activate</b-button>
        <b-button v-if="row.item.active" size="sm" @click="onDeactivate(row.item.uid)">Deactivate</b-button>
        <b-button v-if="!row.item.actual" size="sm" variant="warning" @click="onApply(row.item)">Apply <b-spinner v-if="row.item.applying" small label="Applying..."></b-spinner></b-button>
      </template>
    </b-table>
    <b-overlay :show="busy" no-wrap @shown="onShown" @hidden="onHidden">
      <template #overlay>
        <div v-if="processing" class="text-center p-4 bg-primary text-light rounded">
          <b-icon icon="cloud-upload" font-scale="4"></b-icon>
          <div class="mb-3">Processing...</div>
          <b-progress
            min="1"
            max="20"
            :value="counter"
            variant="success"
            height="3px"
            class="mx-n4 rounded-0"
          ></b-progress>
        </div>
        <div
          v-else
          ref="dialog"
          tabindex="-1"
          role="dialog"
          aria-modal="false"
          aria-labelledby="form-confirm-label"
          class="text-center p-3"
        >
          <p><strong id="form-confirm-label">Are you sure?</strong></p>
          <div class="d-flex">
            <b-button variant="outline-danger" class="mr-3" @click="onCancel">Cancel</b-button>
            <b-button variant="outline-success" @click="onOK">OK</b-button>
          </div>
        </div>
      </template>
    </b-overlay>
  </div>
</div>
</template>

<script>

import { mapState } from 'vuex';

export default {

  data: () => ({
    busy: false,
    processing: false,
    applying: false,
    counter: 1,
    interval: null,
    selectedPid: null,
    projects: projects,
    projectsFile: null,
    fields: [
      {key: 'uid', label: 'uid', sortable: true },
      {key: 'name', label: 'Name', sortable: true },
      {key: 'https', label: 'Https', sortable: true },
      {key: 'backend', label: 'Backend', sortable: true },
      {key: 'template', label: 'Template', sortable: true },
      {key: 'backup', label: 'Backup', sortable: true },
      {key: 'active', label: 'Status', sortable: true },
      {key: 'actions', label: 'Actions'}
    ]
  }),

  computed: {

    localComputed () {

    },

    ...mapState({

      actual: state => state.actual

    })

  },

  methods: {

    onImport(e) {
      e.preventDefault();
      let formData = new FormData();
      formData.append('file', this.projectsFile);

      this.axios.post('/admin/import-projects',
          formData,
          {
          headers: {
              'Content-Type': 'multipart/form-data'
          }
        }
      ).then((response) => {
        let data = response.data
        if (data && data.result === 'ok' && data.projects) {
          this.projects = data.projects
          this.$store.commit('setActual', data.actual)
        }
      })
      .catch(() => {
        console.log('FAILURE!!');
      });

    },

    clearInterval() {
      if (this.interval) {
        clearInterval(this.interval)
        this.interval = null
      }
    },
    onShown() {
      //this.$refs.dialog.focus()
    },
    onHidden() {
      //this.$refs.submit.focus()
    },
    onDelete(pid) {
      this.selectedPid = pid
      this.processing = false
      this.busy = true
    },
    onCancel() {
      this.busy = false
      this.selectedPid = null
    },
    onOK() {
      this.counter = 1
      this.processing = true
      this.clearInterval()
      this.interval = setInterval(() => {
        if (this.counter < 20) {
          this.counter = this.counter + 1
        } else {
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedPid = null
          })
        }
      }, 150)
      this.axios.get('/admin/project/' + this.selectedPid + '/delete')
      .then((response) => {
          let data = response.data
          if (data && data.result === 'ok' && data.projects) {
            this.projects = data.projects
            this.$store.commit('setActual', data.actual)
          }
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedPid = null
          })
      })
      .catch(() => {
        console.log('FAILURE!!');
      });

    },

    onApply(item) {
      if ( !item.applying ) {
        item.applying = true
        this.axios.get('/admin/project/' + item.uid + '/reload')
        .then((response) => {
            let data = response.data
            if (data && data.result === 'ok') {
              item.applying = false
              this.projects = data.projects
            }
        })
        .catch(() => {
          console.log('FAILURE!!');
        });
      }
    },

    onActivate(pid) {
      this.selectedPid = pid
      this.busy = true
      this.counter = 1
      this.processing = true
      this.clearInterval()
      this.interval = setInterval(() => {
        if (this.counter < 20) {
          this.counter = this.counter + 1
        } else {
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedPid = null
          })
        }
      }, 150)
      this.axios.get('/admin/project/' + this.selectedPid + '/activate')
      .then((response) => {
          let data = response.data
          if (data && data.result === 'ok' && data.projects) {
            this.projects = data.projects
            this.$store.commit('setActual', data.actual)
          }
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedPid = null
          })
      })
      .catch(() => {
        console.log('FAILURE!!');
      });
    },

    onDeactivate(pid) {
      this.selectedPid = pid
      this.busy = true
      this.counter = 1
      this.processing = true
      this.clearInterval()
      this.interval = setInterval(() => {
        if (this.counter < 20) {
          this.counter = this.counter + 1
        } else {
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedPid = null
          })
        }
      }, 150)
      this.axios.get('/admin/project/' + this.selectedPid + '/deactivate')
      .then((response) => {
          let data = response.data
          if (data && data.result === 'ok' && data.projects) {
            this.projects = data.projects
            this.$store.commit('setActual', data.actual)
          }
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedPid = null
          })
      })
      .catch(() => {
        console.log('FAILURE!!');
      });
    }

  }

}

</script>
