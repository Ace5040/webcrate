<template>
<div class="admin-page">
  <div class="action-menu">
    <div class="float-right">
      <b-form @submit="onImport">
        <b-form-group>
          <b-form-file
            v-model="redirectsFile"
            :state="Boolean(redirectsFile)"
            placeholder="Choose a file or drop it here..."
            drop-placeholder="Drop file here..."
          ></b-form-file>
          <b-button type="submit" variant="primary">Import</b-button>
        </b-form-group>
      </b-form>
    </div>
    <b-button href="/admin/redirect/add" variant="primary">Create new redirect</b-button>
    <b-spinner v-if="applying" variant="success" label="Applying..."></b-spinner>
  </div>
  <div class="redirects-table position-relative">
    <b-table v-if="redirects.length" sort-by="name" striped hover :items="redirects" :fields="fields">
      <template v-slot:cell(name)="row">
        {{ row.value }}
      </template>
      <template v-slot:cell(active)="row">
        <b-badge :variant="row.value?'success':'warning'">{{row.value?'active':'inactive'}}</b-badge>
      </template>
      <template v-slot:cell(actions)="row">
        <b-button variant="primary" size="sm" :href="'/admin/redirect/'+row.item.name">Edit</b-button>
        <b-button variant="danger" size="sm" @click="onDelete(row.item.name)">Delete</b-button>
        <b-button v-if="row.item.active == false" variant="success" size="sm" @click="onActivate(row.item.name)">Activate</b-button>
        <b-button v-if="row.item.active" size="sm" @click="onDeactivate(row.item.name)">Deactivate</b-button>
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
    selectedName: null,
    redirects: redirects,
    redirectsFile: null,
    fields: [
      {key: 'name', label: 'Name', sortable: true },
      {key: 'url', label: 'Url', sortable: true },
      {key: 'https', label: 'Https', sortable: true },
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
      formData.append('file', this.redirectsFile);

      this.axios.post('/admin/import-redirects',
          formData,
          {
          headers: {
              'Content-Type': 'multipart/form-data'
          }
        }
      ).then((response) => {
        let data = response.data
        if (data && data.result === 'ok' && data.redirects) {
          this.redirects = data.redirects
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
    onDelete(name) {
      this.selectedName = name
      this.processing = false
      this.busy = true
    },
    onCancel() {
      this.busy = false
      this.selectedName = null
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
            this.selectedName = null
          })
        }
      }, 150)
      this.axios.get('/admin/redirect/' + this.selectedName + '/delete')
      .then((response) => {
          let data = response.data
          if (data && data.result === 'ok' && data.redirects) {
            this.redirects = data.redirects
            this.$store.commit('setActual', data.actual)
          }
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedName = null
          })
      })
      .catch(() => {
        console.log('FAILURE!!');
      });

    },

    onApply(item) {
      if ( !item.applying ) {
        item.applying = true
        this.axios.get('/admin/redirect/' + item.name + '/reload')
        .then((response) => {
            let data = response.data
            if (data && data.result === 'ok') {
              item.applying = false
              this.redirects = data.redirects
            }
        })
        .catch(() => {
          console.log('FAILURE!!');
        });
      }
    },

    onActivate(name) {
      this.selectedName = name
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
            this.selectedName = null
          })
        }
      }, 150)
      this.axios.get('/admin/redirect/' + this.selectedName + '/activate')
      .then((response) => {
          let data = response.data
          if (data && data.result === 'ok' && data.redirects) {
            this.redirects = data.redirects
            this.$store.commit('setActual', data.actual)
          }
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedName = null
          })
      })
      .catch(() => {
        console.log('FAILURE!!');
      });
    },

    onDeactivate(name) {
      this.selectedName = name
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
            this.selectedName = null
          })
        }
      }, 150)
      this.axios.get('/admin/redirect/' + this.selectedName + '/deactivate')
      .then((response) => {
          let data = response.data
          if (data && data.result === 'ok' && data.redirects) {
            this.redirects = data.redirects
            this.$store.commit('setActual', data.actual)
          }
          this.clearInterval()
          this.$nextTick(() => {
            this.busy = this.processing = false
            this.selectedName = null
          })
      })
      .catch(() => {
        console.log('FAILURE!!');
      });
    }

  }

}

</script>
