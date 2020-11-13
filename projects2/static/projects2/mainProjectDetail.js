var app = new Vue({
  el: '#app',
  delimiters: ["${", "}"],
  data: {
    showOverview: true,

    py_loading: false,
    projectYear: {},

    // staff
    staff_loading: false,
    staff: [],
    staffToEdit: {},
    showNewStaffModal: false,
    showOldStaffModal: false,

    // om costs
    om_cost_loading: false,
    om_costs: [],
    omCostToEdit: {},
    showNewOMCostModal: false,
    showOldOMCostModal: false,

    // capital costs
    capital_cost_loading: false,
    capital_costs: [],
    capitalCostToEdit: {},
    showNewCapitalCostModal: false,
    showOldCapitalCostModal: false,

    // milestones
    milestone_loading: false,
    milestones: [],
    milestoneToEdit: {},
    showNewMilestoneModal: false,
    showOldMilestoneModal: false,

  },
  methods: {
    displayOverview() {
      this.showOverview = true
    },
    displayProjectYear(yearId) {
      this.showOverview = false
      this.getProjectYear(yearId)
    },
    getProjectYear(yearId) {
      this.py_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/`;
      apiService(endpoint)
          .then(response => {
            this.py_loading = false;
            this.projectYear = response;
            // now let's get all the related data
            this.getStaff(yearId)
            this.getOMCosts(yearId)
            this.getCapitalCosts(yearId)
            this.getMilestones(yearId)
          })
    },

    // Staff
    getStaff(yearId) {
      this.staff_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/staff/`;
      apiService(endpoint)
          .then(response => {
            this.staff_loading = false;
            this.staff = response;
          })
    },
    deleteStaffMember(staffMember) {
      userInput = confirm(deleteMsg)
      if (userInput) {
        let endpoint = `/api/project-planning/staff/${staffMember.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.$delete(this.staff, this.staff.indexOf(staffMember));
            })
      }
    },
    openStaffModal(staff = null) {
      if (!staff) {
        this.showNewStaffModal = true;
      } else {
        this.staffToEdit = staff;
        this.showOldStaffModal = true;
      }

    },

    // O&M
    getOMCosts(yearId) {
      this.om_cost_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/om-costs/`;
      apiService(endpoint)
          .then(response => {
            this.om_cost_loading = false;
            this.om_costs = response;
          })
    },
    deleteOMCost(OMCost) {
      userInput = confirm(deleteMsg + OMCost.om_category_display)
      if (userInput) {
        let endpoint = `/api/project-planning/om-costs/${OMCost.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.$delete(this.om_costs, this.om_costs.indexOf(OMCost));
            })
      }
    },
    addAllOMCosts() {
      if (this.projectYear.id) {
        this.om_cost_loading = true;
        let endpoint = `/api/project-planning/project-years/${this.projectYear.id}/add-all-costs/`;
        apiService(endpoint, "POST")
            .then(response => {
              this.om_cost_loading = false;
              this.om_costs = response;
            })
      }
    },
    clearEmptyOMCosts() {
      if (this.projectYear.id) {
        this.om_cost_loading = true;
        let endpoint = `/api/project-planning/project-years/${this.projectYear.id}/remove-empty-costs/`;
        apiService(endpoint, "POST")
            .then(response => {
              this.om_cost_loading = false;
              this.om_costs = response;
            })
      }
    },
    openOMCostModal(OMCost) {
      if (!OMCost) {
        this.showNewOMCostModal = true;
      } else {
        this.omCostToEdit = OMCost;
        this.showOldOMCostModal = true;
      }

    },

    // Capital
    getCapitalCosts(yearId) {
      this.capital_cost_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/capital-costs/`;
      apiService(endpoint)
          .then(response => {
            this.capital_cost_loading = false;
            this.capital_costs = response;
          })
    },
    deleteCapitalCost(capitalCost) {
      userInput = confirm(deleteMsg + capitalCost.category_display)
      if (userInput) {
        let endpoint = `/api/project-planning/capital-costs/${capitalCost.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.$delete(this.capital_costs, this.capital_costs.indexOf(capitalCost));
            })
      }
    },

    openCapitalCostModal(capitalCost) {
      if (!capitalCost) {
        this.showNewCapitalCostModal = true;
      } else {
        this.capitalCostToEdit = capitalCost;
        this.showOldCapitalCostModal = true;
      }
    },

    // Milestones
    getMilestones(yearId) {
      this.milestone_loading = true;
      let endpoint = `/api/project-planning/project-years/${yearId}/milestones/`;
      apiService(endpoint)
          .then(response => {
            this.milestone_loading = false;
            this.milestones = response;
          })
    },
    deleteMilestone(milestone) {
      userInput = confirm(deleteMsg + milestone.name)
      if (userInput) {
        let endpoint = `/api/project-planning/milestones/${milestone.id}/`;
        apiService(endpoint, "DELETE")
            .then(response => {
              this.$delete(this.milestones, this.milestones.indexOf(milestone));
            })
      }
    },

    openMilestoneModal(milestone) {
      if (!milestone) {
        this.showNewMilestoneModal = true;
      } else {
        this.milestoneToEdit = milestone;
        this.showOldMilestoneModal = true;
      }
    },



    closeModals(projectYear) {
      this.showNewStaffModal = false;
      this.showOldStaffModal = false;

      this.showNewOMCostModal = false;
      this.showOldOMCostModal = false;

      this.showNewCapitalCostModal = false;
      this.showOldCapitalCostModal = false;

      this.showNewMilestoneModal = false;
      this.showOldMilestoneModal = false;

      if (projectYear) {
        this.$nextTick(() => {
          this.getStaff(projectYear.id)
          this.getOMCosts(projectYear.id)
          this.getCapitalCosts(projectYear.id)
          this.getMilestones(projectYear.id)

        })
      }
    },
    goProjectYearEdit(projectYearId) {
      window.location.href = `/project-planning/project-year/${projectYearId}/edit/`
    },
    goProjectYearDelete(projectYearId) {
      window.location.href = `/project-planning/project-year/${projectYearId}/delete/`
    },
    goProjectYearClone(projectYearId) {
      window.location.href = `/project-planning/project-year/${projectYearId}/clone/`
    },
    isABase(name) {
      if (name && name.length) {
        return name.toLowerCase().search("a-base") > -1
      }
    },
    isBBase(name) {
      if (name && name.length) {
        return name.toLowerCase().search("b-base") > -1
      }
    },
    isCBase(name) {
      if (name && name.length) {
        return name.toLowerCase().search("c-base") > -1
      }
    },

  },

  filters: {
    floatformat: function (value, precision = 2) {
      if (value == null) return '';
      value = Number(value).toFixed(precision);
      return value
    },
    zero2NullMark: function (value) {
      if (!value || value === "0.00" || value == 0) return '---';
      return value
    },
    nz: function (value, arg = "---") {
      if (value == null || value === "None") return arg;
      return value
    },
    yesNo: function (value) {
      if (value == null || value == false || value == 0) return 'No';
      return "Yes"
    },
    percentage: function (value, decimals) {
      // https://gist.github.com/belsrc/672b75d1f89a9a5c192c
      if (!value) {
        value = 0;
      }

      if (!decimals) {
        decimals = 0;
      }

      value = value * 100;
      value = Math.round(value * Math.pow(10, decimals)) / Math.pow(10, decimals);
      value = value + '%';
      return value;
    }
  },
  computed: {},
  created() {
  },
  mounted() {
  },
});

