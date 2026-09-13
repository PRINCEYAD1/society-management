import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

void main() {
  runApp(const SocietyApp());
}

class SocietyApp extends StatelessWidget {
  const SocietyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Society Management',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed: Colors.indigo,
      ),
      home: const LoginScreen(),
    );
  }
}

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();

  final _storage = const FlutterSecureStorage();

  bool _isLoading = false;
  bool _obscurePassword = true;

  final String baseUrl = 'http://10.0.2.2:8000/api';

  Future<void> _login() async {
    // Prevent duplicate login requests caused by repeated taps.
    if (_isLoading) return;

    final username = _usernameController.text.trim();
    final password = _passwordController.text;

    if (username.isEmpty || password.isEmpty) {
      _showMessage('Please enter username and password.');
      return;
    }

    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    bool navigationStarted = false;

    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/auth/login/'),
            headers: {
              'Content-Type': 'application/json',
            },
            body: jsonEncode({
              'username': username,
              'password': password,
            }),
          )
          .timeout(const Duration(seconds: 20));

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200 &&
          data is Map<String, dynamic> &&
          data['success'] == true) {
        final accessToken = data['access']?.toString();
        final refreshToken = data['refresh']?.toString();
        final user = data['user'];

        if (accessToken == null ||
            accessToken.isEmpty ||
            refreshToken == null ||
            refreshToken.isEmpty ||
            user is! Map) {
          if (mounted) {
            _showMessage('Login response is incomplete.');
          }
          return;
        }

        final role =
            (user['role']?.toString() ?? '').trim().toUpperCase();
        final loggedInUsername =
            (user['username']?.toString() ?? username).trim();

        if (!{'ADMIN', 'SECURITY', 'RESIDENT'}.contains(role)) {
          if (mounted) {
            _showMessage('Unknown user role: $role');
          }
          return;
        }

        // Clear stale session values before writing the new session.
        await _storage.deleteAll();

        await _storage.write(
          key: 'access_token',
          value: accessToken,
        );
        await _storage.write(
          key: 'refresh_token',
          value: refreshToken,
        );
        await _storage.write(
          key: 'role',
          value: role,
        );
        await _storage.write(
          key: 'username',
          value: loggedInUsername,
        );

        if (!mounted) return;

        Widget destination;
        switch (role) {
          case 'ADMIN':
            destination = AdminDashboardScreen(
              username: loggedInUsername,
            );
            break;
          case 'SECURITY':
            destination = SecurityDashboardScreen(
              username: loggedInUsername,
            );
            break;
          case 'RESIDENT':
            destination = ResidentDashboardScreen(
              username: loggedInUsername,
            );
            break;
          default:
            return;
        }

        // Finish the loading state before removing LoginScreen.
        setState(() {
          _isLoading = false;
        });

        navigationStarted = true;

        // Remove the login route completely so the old LoginScreen
        // cannot rebuild during/after Admin dashboard navigation.
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(
            builder: (_) => destination,
          ),
          (route) => false,
        );
        return;
      }

      if (mounted) {
        String message = 'Login failed.';
        if (data is Map && data['message'] != null) {
          message = data['message'].toString();
        } else if (response.statusCode == 401) {
          message = 'Invalid username or password.';
        } else if (response.statusCode == 403) {
          message = 'This account is not allowed to sign in.';
        } else if (response.statusCode >= 500) {
          message = 'Server error. Please try again.';
        }
        _showMessage(message);
      }
    } catch (_) {
      if (mounted) {
        _showMessage(
          'Unable to connect to the server. Please try again.',
        );
      }
    } finally {
      // Do not rebuild LoginScreen after navigation has started.
      if (mounted && !navigationStarted && _isLoading) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
      ),
    );
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(
                maxWidth: 420,
              ),
              child: Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(
                        Icons.apartment,
                        size: 72,
                      ),
                      const SizedBox(height: 16),

                      Text(
                        'Society Management',
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),

                      const SizedBox(height: 8),

                      const Text(
                        'Sign in to continue',
                      ),

                      const SizedBox(height: 28),

                      TextField(
                        controller: _usernameController,
                        decoration: const InputDecoration(
                          labelText: 'Username',
                          prefixIcon: Icon(Icons.person),
                          border: OutlineInputBorder(),
                        ),
                      ),

                      const SizedBox(height: 16),

                      TextField(
                        controller: _passwordController,
                        obscureText: _obscurePassword,
                        onSubmitted: (_) => _login(),
                        decoration: InputDecoration(
                          labelText: 'Password',
                          prefixIcon: const Icon(Icons.lock),
                          border: const OutlineInputBorder(),
                          suffixIcon: IconButton(
                            onPressed: () {
                              setState(() {
                                _obscurePassword =
                                    !_obscurePassword;
                              });
                            },
                            icon: Icon(
                              _obscurePassword
                                  ? Icons.visibility
                                  : Icons.visibility_off,
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 24),

                      SizedBox(
                        width: double.infinity,
                        height: 50,
                        child: FilledButton(
                          onPressed:
                              _isLoading ? null : _login,
                          child: _isLoading
                              ? const SizedBox(
                                  height: 22,
                                  width: 22,
                                  child:
                                      CircularProgressIndicator(
                                    strokeWidth: 2,
                                  ),
                                )
                              : const Text('Login'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}


class AdminDashboardScreen extends StatefulWidget {
  final String username;

  const AdminDashboardScreen({
    super.key,
    required this.username,
  });

  @override
  State<AdminDashboardScreen> createState() =>
      _AdminDashboardScreenState();
}

class _AdminDashboardScreenState
    extends State<AdminDashboardScreen> {
  final _storage = const FlutterSecureStorage();
  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  String? _error;
  Map<String, dynamic>? _dashboard;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    if (!mounted) return;

    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'access_token');

      if (token == null) {
        if (!mounted) return;
        setState(() {
          _error = 'Login token not found.';
          _isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/dashboard/admin/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      final data = jsonDecode(response.body);

      if (!mounted) return;

      if (response.statusCode == 200 &&
          data is Map<String, dynamic> &&
          data['success'] == true &&
          data['dashboard'] is Map) {
        setState(() {
          _dashboard = Map<String, dynamic>.from(
            data['dashboard'] as Map,
          );
          _isLoading = false;
        });
      } else if (response.statusCode == 401) {
        // Token is invalid/expired. Return to login safely.
        await _storage.deleteAll();
        if (!mounted) return;
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(
            builder: (_) => const LoginScreen(),
          ),
          (route) => false,
        );
      } else {
        setState(() {
          _error = data is Map && data['message'] != null
              ? data['message'].toString()
              : 'Unable to load dashboard.';
          _isLoading = false;
        });
      }
    } catch (_) {
      if (!mounted) return;
      setState(() {
        _error = 'Unable to connect to the server.';
        _isLoading = false;
      });
    }
  }

  Future<void> _logout() async {
    await _storage.deleteAll();
    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => const LoginScreen(),
      ),
      (route) => false,
    );
  }

  Future<void> _openAdminModule(
    AdminModuleType module,
  ) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AdminModuleScreen(
          module: module,
        ),
      ),
    );

    if (mounted) {
      _loadDashboard();
    }
  }

  void _showSummaryOnly(String title) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          '$title is available as a dashboard summary. '
          'A dedicated mobile API endpoint is not implemented yet.',
        ),
      ),
    );
  }

  // Responsive Admin dashboard card for Android and web.
  Widget _dashboardCard({
    required String title,
    required String value,
    required IconData icon,
    AdminModuleType? module,
  }) {
    return Card(
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: module == null
            ? () => _showSummaryOnly(title)
            : () => _openAdminModule(module),
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: 10,
            vertical: 12,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 30),
              const SizedBox(height: 7),
              FittedBox(
                fit: BoxFit.scaleDown,
                child: Text(
                  value,
                  maxLines: 1,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(height: 5),
              Text(
                title,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 13,
                  height: 1.15,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _serviceTile({
    required String title,
    required IconData icon,
    required AdminModuleType module,
  }) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          child: Icon(icon),
        ),
        title: Text(title),
        trailing: const Icon(Icons.chevron_right),
        onTap: () => _openAdminModule(module),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Admin Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadDashboard,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Logout',
            onPressed: _logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment:
                        MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 50,
                      ),
                      const SizedBox(height: 12),
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _loadDashboard,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadDashboard,
                  child: ListView(
                    padding: const EdgeInsets.all(20),
                    children: [
                      Text(
                        'Welcome, ${widget.username}',
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 6),
                      const Text('Role: ADMIN'),
                      const SizedBox(height: 24),
                      Text(
                        'Society Overview',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 12),
                      GridView.count(
                        crossAxisCount:
                            MediaQuery.of(context).size.width >
                                    900
                                ? 4
                                : 2,
                        shrinkWrap: true,
                        physics:
                            const NeverScrollableScrollPhysics(),
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 1.0,
                        children: [
                          _dashboardCard(
                            title: 'Total Flats',
                            value:
                                '${_dashboard?['total_flats'] ?? 0}',
                            icon: Icons.apartment,
                            module: AdminModuleType.flats,
                          ),
                          _dashboardCard(
                            title: 'Total Residents',
                            value:
                                '${_dashboard?['total_residents'] ?? 0}',
                            icon: Icons.people,
                            module: AdminModuleType.residents,
                          ),
                          _dashboardCard(
                            title: 'Pending Invoices',
                            value:
                                '${_dashboard?['pending_invoices'] ?? 0}',
                            icon: Icons.receipt_long,
                            module: AdminModuleType.invoices,
                          ),
                          _dashboardCard(
                            title: 'Outstanding Amount',
                            value:
                                '₹${_dashboard?['outstanding_amount'] ?? 0}',
                            icon:
                                Icons.account_balance_wallet,
                            module: AdminModuleType.invoices,
                          ),
                          _dashboardCard(
                            title: 'Collection This Month',
                            value:
                                '₹${_dashboard?['collection_this_month'] ?? 0}',
                            icon: Icons.payments,
                            module: AdminModuleType.payments,
                          ),
                          _dashboardCard(
                            title: 'Monthly Expenses',
                            value:
                                '₹${_dashboard?['monthly_expenses'] ?? 0}',
                            icon: Icons.money_off_csred,
                            module: AdminModuleType.expenses,
                          ),
                          _dashboardCard(
                            title: 'Open Complaints',
                            value:
                                '${_dashboard?['open_complaints'] ?? 0}',
                            icon: Icons.report_problem,
                            module: AdminModuleType.complaints,
                          ),
                          _dashboardCard(
                            title: 'Visitors Today',
                            value:
                                '${_dashboard?['visitors_today'] ?? 0}',
                            icon: Icons.badge,
                            module: AdminModuleType.visitors,
                          ),
                          _dashboardCard(
                            title: 'Parcels Waiting',
                            value:
                                '${_dashboard?['parcels_waiting'] ?? 0}',
                            icon: Icons.inventory_2,
                            module: AdminModuleType.parcels,
                          ),
                          _dashboardCard(
                            title: 'Active Vehicles',
                            value:
                                '${_dashboard?['active_vehicles'] ?? 0}',
                            icon: Icons.directions_car,
                            module: AdminModuleType.vehicles,
                          ),
                          _dashboardCard(
                            title: 'Domestic Workers',
                            value:
                                '${_dashboard?['active_domestic_workers'] ?? 0}',
                            icon: Icons.badge_outlined,
                            module:
                                AdminModuleType.domesticWorkers,
                          ),
                          _dashboardCard(
                            title: 'Pending Certificates',
                            value:
                                '${_dashboard?['pending_certificate_requests'] ?? 0}',
                            icon: Icons.description,
                            module:
                                AdminModuleType.certificates,
                          ),
                          _dashboardCard(
                            title: 'Move Requests',
                            value:
                                '${_dashboard?['pending_move_requests'] ?? 0}',
                            icon: Icons.local_shipping,
                            module:
                                AdminModuleType.moveRequests,
                          ),
                          _dashboardCard(
                            title: 'Active AMCs',
                            value:
                                '${_dashboard?['active_amcs'] ?? 0}',
                            icon: Icons.handyman,
                            module: AdminModuleType.vendorAmc,
                          ),
                          _dashboardCard(
                            title: 'Active Assets',
                            value:
                                '${_dashboard?['active_assets'] ?? 0}',
                            icon:
                                Icons.precision_manufacturing,
                            module: AdminModuleType.assets,
                          ),
                          _dashboardCard(
                            title: 'Active Polls',
                            value:
                                '${_dashboard?['active_polls'] ?? 0}',
                            icon: Icons.poll,
                            module: AdminModuleType.polls,
                          ),
                          _dashboardCard(
                            title: 'Upcoming Events',
                            value:
                                '${_dashboard?['upcoming_events'] ?? 0}',
                            icon: Icons.event,
                            module: AdminModuleType.events,
                          ),
                          _dashboardCard(
                            title: 'Lost & Found',
                            value:
                                '${_dashboard?['open_lost_found'] ?? 0}',
                            icon: Icons.search,
                            module: AdminModuleType.lostFound,
                          ),
                          _dashboardCard(
                            title: 'Meetings',
                            value:
                                '${_dashboard?['upcoming_meetings'] ?? 0}',
                            icon: Icons.groups,
                            module: AdminModuleType.meetings,
                          ),
                          _dashboardCard(
                            title: 'Amenity Bookings',
                            value:
                                '${_dashboard?['pending_amenity_bookings'] ?? 0}',
                            icon: Icons.pool,
                            module:
                                AdminModuleType.amenityBookings,
                          ),
                        ],
                      ),
                      const SizedBox(height: 28),
                      Text(
                        'Admin Services',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 10),
                      _serviceTile(
                        title: 'Notices',
                        icon: Icons.campaign,
                        module: AdminModuleType.notices,
                      ),
                      _serviceTile(
                        title: 'Payments',
                        icon: Icons.payments_outlined,
                        module: AdminModuleType.payments,
                      ),
                      _serviceTile(
                        title: 'Amenities',
                        icon: Icons.pool,
                        module: AdminModuleType.amenities,
                      ),
                      _serviceTile(
                        title: 'Worker Attendance',
                        icon: Icons.how_to_reg,
                        module: AdminModuleType.attendance,
                      ),
                      _serviceTile(
                        title: 'Emergency Contacts',
                        icon: Icons.emergency,
                        module:
                            AdminModuleType.emergencyContacts,
                      ),
                      const SizedBox(height: 30),
                    ],
                  ),
                ),
    );
  }
}

enum AdminModuleType {
  flats,
  residents,
  lostFound,
  notices,
  complaints,
  visitors,
  invoices,
  payments,
  amenities,
  amenityBookings,
  parcels,
  vehicles,
  domesticWorkers,
  attendance,
  certificates,
  moveRequests,
  events,
  meetings,
  assets,
  vendorAmc,
  expenses,
  emergencyContacts,
  polls,
}

class AdminModuleScreen extends StatefulWidget {
  final AdminModuleType module;

  const AdminModuleScreen({
    super.key,
    required this.module,
  });

  @override
  State<AdminModuleScreen> createState() =>
      _AdminModuleScreenState();
}

class _AdminModuleScreenState
    extends State<AdminModuleScreen> {
  final _storage = const FlutterSecureStorage();
  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _error;
  String _search = '';
  List<dynamic> _items = [];

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  String get _title {
    switch (widget.module) {
      case AdminModuleType.flats:
        return 'Flats';
      case AdminModuleType.residents:
        return 'Residents';
      case AdminModuleType.lostFound:
        return 'Lost & Found';
      case AdminModuleType.notices:
        return 'Notices';
      case AdminModuleType.complaints:
        return 'Complaints';
      case AdminModuleType.visitors:
        return 'Visitors';
      case AdminModuleType.invoices:
        return 'Invoices';
      case AdminModuleType.payments:
        return 'Payments';
      case AdminModuleType.amenities:
        return 'Amenities';
      case AdminModuleType.amenityBookings:
        return 'Amenity Bookings';
      case AdminModuleType.parcels:
        return 'Parcels';
      case AdminModuleType.vehicles:
        return 'Vehicles';
      case AdminModuleType.domesticWorkers:
        return 'Domestic Workers';
      case AdminModuleType.attendance:
        return 'Worker Attendance';
      case AdminModuleType.certificates:
        return 'Certificate Requests';
      case AdminModuleType.moveRequests:
        return 'Move Requests';
      case AdminModuleType.events:
        return 'Events';
      case AdminModuleType.meetings:
        return 'Meetings';
      case AdminModuleType.assets:
        return 'Assets';
      case AdminModuleType.vendorAmc:
        return 'Vendor / AMC';
      case AdminModuleType.expenses:
        return 'Expenses';
      case AdminModuleType.emergencyContacts:
        return 'Emergency Contacts';
      case AdminModuleType.polls:
        return 'Polls';
    }
  }

  String get _endpoint {
    switch (widget.module) {
      case AdminModuleType.flats:
        return 'flats/';
      case AdminModuleType.residents:
        return 'residents/';
      case AdminModuleType.lostFound:
        return 'lost-found/';
      case AdminModuleType.notices:
        return 'notices/';
      case AdminModuleType.complaints:
        return 'complaints/';
      case AdminModuleType.visitors:
        return 'visitors/';
      case AdminModuleType.invoices:
        return 'billing/invoices/';
      case AdminModuleType.payments:
        return 'billing/payments/';
      case AdminModuleType.amenities:
        return 'amenities/';
      case AdminModuleType.amenityBookings:
        return 'amenities/bookings/';
      case AdminModuleType.parcels:
        return 'parcels/';
      case AdminModuleType.vehicles:
        return 'vehicles/';
      case AdminModuleType.domesticWorkers:
        return 'domestic-workers/';
      case AdminModuleType.attendance:
        return 'domestic-workers/attendance/';
      case AdminModuleType.certificates:
        return 'certificate-requests/';
      case AdminModuleType.moveRequests:
        return 'move-requests/';
      case AdminModuleType.events:
        return 'events/';
      case AdminModuleType.meetings:
        return 'meetings/';
      case AdminModuleType.assets:
        return 'assets/';
      case AdminModuleType.vendorAmc:
        return 'vendor-amc/';
      case AdminModuleType.expenses:
        return 'expenses/';
      case AdminModuleType.emergencyContacts:
        return 'emergency-contacts/';
      case AdminModuleType.polls:
        return 'polls/';
    }
  }

  String get _responseKey {
    switch (widget.module) {
      case AdminModuleType.flats:
        return 'flats';
      case AdminModuleType.residents:
        return 'residents';
      case AdminModuleType.lostFound:
        return 'lost_found';
      case AdminModuleType.notices:
        return 'notices';
      case AdminModuleType.complaints:
        return 'complaints';
      case AdminModuleType.visitors:
        return 'visitors';
      case AdminModuleType.invoices:
        return 'invoices';
      case AdminModuleType.payments:
        return 'payments';
      case AdminModuleType.amenities:
        return 'amenities';
      case AdminModuleType.amenityBookings:
        return 'bookings';
      case AdminModuleType.parcels:
        return 'parcels';
      case AdminModuleType.vehicles:
        return 'vehicles';
      case AdminModuleType.domesticWorkers:
        return 'workers';
      case AdminModuleType.attendance:
        return 'attendance';
      case AdminModuleType.certificates:
        return 'certificate_requests';
      case AdminModuleType.moveRequests:
        return 'move_requests';
      case AdminModuleType.events:
        return 'events';
      case AdminModuleType.meetings:
        return 'meetings';
      case AdminModuleType.assets:
        return 'assets';
      case AdminModuleType.vendorAmc:
        return 'vendors';
      case AdminModuleType.expenses:
        return 'expenses';
      case AdminModuleType.emergencyContacts:
        return 'contacts';
      case AdminModuleType.polls:
        return 'polls';
    }
  }

  IconData get _icon {
    switch (widget.module) {
      case AdminModuleType.flats:
        return Icons.apartment;
      case AdminModuleType.residents:
        return Icons.people;
      case AdminModuleType.lostFound:
        return Icons.search;
      case AdminModuleType.notices:
        return Icons.campaign;
      case AdminModuleType.complaints:
        return Icons.report_problem;
      case AdminModuleType.visitors:
        return Icons.people;
      case AdminModuleType.invoices:
        return Icons.receipt_long;
      case AdminModuleType.payments:
        return Icons.payments;
      case AdminModuleType.amenities:
      case AdminModuleType.amenityBookings:
        return Icons.pool;
      case AdminModuleType.parcels:
        return Icons.inventory_2;
      case AdminModuleType.vehicles:
        return Icons.directions_car;
      case AdminModuleType.domesticWorkers:
      case AdminModuleType.attendance:
        return Icons.badge;
      case AdminModuleType.certificates:
        return Icons.description;
      case AdminModuleType.moveRequests:
        return Icons.local_shipping;
      case AdminModuleType.events:
        return Icons.event;
      case AdminModuleType.meetings:
        return Icons.groups;
      case AdminModuleType.assets:
        return Icons.precision_manufacturing;
      case AdminModuleType.vendorAmc:
        return Icons.handyman;
      case AdminModuleType.expenses:
        return Icons.money_off_csred;
      case AdminModuleType.emergencyContacts:
        return Icons.emergency;
      case AdminModuleType.polls:
        return Icons.poll;
    }
  }

  bool get _canCreate {
    return {
      AdminModuleType.flats,
      AdminModuleType.residents,
      AdminModuleType.lostFound,
      AdminModuleType.notices,
      AdminModuleType.visitors,
      AdminModuleType.invoices,
      AdminModuleType.payments,
      AdminModuleType.parcels,
      AdminModuleType.vehicles,
      AdminModuleType.domesticWorkers,
      AdminModuleType.events,
      AdminModuleType.meetings,
      AdminModuleType.assets,
      AdminModuleType.vendorAmc,
      AdminModuleType.expenses,
      AdminModuleType.emergencyContacts,
      AdminModuleType.polls,
    }.contains(widget.module);
  }

  Future<String?> _token() {
    return _storage.read(key: 'access_token');
  }

  Map<String, String> _headers(String token) {
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  String _messageFromData(
    dynamic data,
    String fallback,
  ) {
    if (data is Map<String, dynamic>) {
      if (data['message'] != null) {
        return data['message'].toString();
      }
      if (data['detail'] != null) {
        return data['detail'].toString();
      }
      if (data['errors'] != null) {
        return data['errors'].toString();
      }
    }
    return fallback;
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _loadItems() async {
    if (mounted) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      final token = await _token();

      if (token == null) {
        if (mounted) {
          setState(() {
            _error = 'Login token not found.';
            _isLoading = false;
          });
        }
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/$_endpoint'),
        headers: _headers(token),
      );

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200) {
        List<dynamic> items = [];

        if (data is Map<String, dynamic>) {
          final preferred = data[_responseKey];
          if (preferred is List) {
            items = preferred;
          } else {
            for (final value in data.values) {
              if (value is List) {
                items = value;
                break;
              }
            }
          }
        } else if (data is List) {
          items = data;
        }

        if (mounted) {
          setState(() {
            _items = items;
            _isLoading = false;
          });
        }
      } else {
        if (mounted) {
          setState(() {
            _error =
                '${_messageFromData(data, 'Unable to load $_title.')} '
                '(HTTP ${response.statusCode})';
            _isLoading = false;
          });
        }
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _error = 'Unable to connect to the server.';
          _isLoading = false;
        });
      }
    }
  }

  Future<bool> _request({
    required String method,
    required String endpoint,
    required Map<String, dynamic> body,
  }) async {
    if (_isSubmitting) return false;

    setState(() => _isSubmitting = true);

    try {
      final token = await _token();

      if (token == null) {
        _showMessage('Login token not found.');
        return false;
      }

      late http.Response response;
      final uri = Uri.parse('$baseUrl/$endpoint');

      if (method == 'POST') {
        response = await http.post(
          uri,
          headers: _headers(token),
          body: jsonEncode(body),
        );
      } else {
        response = await http.patch(
          uri,
          headers: _headers(token),
          body: jsonEncode(body),
        );
      }

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode >= 200 &&
          response.statusCode < 300) {
        _showMessage(
          data is Map<String, dynamic> &&
                  data['message'] != null
              ? data['message'].toString()
              : 'Saved successfully.',
        );
        await _loadItems();
        return true;
      }

      _showMessage(
        _messageFromData(
          data,
          'Request failed (HTTP ${response.statusCode}).',
        ),
      );
      return false;
    } catch (_) {
      _showMessage('Unable to connect to the server.');
      return false;
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  Future<void> _patchItem(
    Map<String, dynamic> item,
    Map<String, dynamic> changes,
  ) async {
    final id = item['id'];
    if (id == null) return;

    String endpoint = '$_endpoint$id/';

    await _request(
      method: 'PATCH',
      endpoint: endpoint,
      body: changes,
    );
  }

  List<Map<String, dynamic>> _formFields() {
    switch (widget.module) {
      case AdminModuleType.flats:
        return [
          {
            'key': 'building',
            'label': 'Building ID *',
            'number': true,
          },
          {'key': 'flat_number', 'label': 'Flat number *'},
          {'key': 'floor', 'label': 'Floor *', 'number': true},
          {
            'key': 'area_sqft',
            'label': 'Area (sq ft)',
            'number': true,
          },
          {
            'key': 'ownership_type',
            'label': 'Ownership (OWNER/RENTED/VACANT) *',
          },
        ];
      case AdminModuleType.residents:
        return [
          {'key': 'username', 'label': 'Username *'},
          {'key': 'password', 'label': 'Password *'},
          {'key': 'first_name', 'label': 'First name'},
          {'key': 'last_name', 'label': 'Last name'},
          {'key': 'email', 'label': 'Email'},
          {'key': 'phone_number', 'label': 'Phone'},
          {'key': 'flat', 'label': 'Flat ID', 'number': true},
          {
            'key': 'is_primary_contact',
            'label': 'Primary contact',
            'bool': true,
            'default': true,
          },
          {
            'key': 'move_in_date',
            'label': 'Move-in date (YYYY-MM-DD)',
          },
          {
            'key': 'emergency_contact_name',
            'label': 'Emergency contact name',
          },
          {
            'key': 'emergency_contact_phone',
            'label': 'Emergency contact phone',
          },
          {
            'key': 'is_active',
            'label': 'Active account',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.lostFound:
        return [
          {
            'key': 'item_type',
            'label': 'Type (LOST/FOUND) *',
          },
          {'key': 'title', 'label': 'Title *'},
          {
            'key': 'description',
            'label': 'Description',
            'lines': 3,
          },
          {'key': 'location', 'label': 'Location'},
          {
            'key': 'status',
            'label': 'Status (OPEN/CLAIMED/CLOSED)',
          },
        ];
      case AdminModuleType.notices:
        return [
          {'key': 'title', 'label': 'Title *'},
          {
            'key': 'content',
            'label': 'Content *',
            'lines': 4,
          },
          {'key': 'category', 'label': 'Category'},
          {
            'key': 'pinned',
            'label': 'Pinned',
            'bool': true,
          },
        ];
      case AdminModuleType.visitors:
        return [
          {'key': 'name', 'label': 'Visitor name *'},
          {'key': 'phone_number', 'label': 'Phone'},
          {'key': 'purpose', 'label': 'Purpose'},
          {
            'key': 'visiting_flat',
            'label': 'Flat ID *',
            'number': true,
          },
          {
            'key': 'vehicle_number',
            'label': 'Vehicle number',
          },
        ];
      case AdminModuleType.invoices:
        return [
          {
            'key': 'flat',
            'label': 'Flat ID *',
            'number': true,
          },
          {'key': 'title', 'label': 'Title *'},
          {
            'key': 'amount',
            'label': 'Amount *',
            'decimal': true,
          },
          {
            'key': 'due_date',
            'label': 'Due date (YYYY-MM-DD) *',
          },
          {'key': 'notes', 'label': 'Notes', 'lines': 3},
        ];
      case AdminModuleType.payments:
        return [
          {
            'key': 'invoice',
            'label': 'Invoice ID *',
            'number': true,
          },
          {
            'key': 'amount',
            'label': 'Amount *',
            'decimal': true,
          },
          {
            'key': 'method',
            'label': 'Method (CASH/UPI/BANK/OTHER) *',
          },
          {
            'key': 'reference_number',
            'label': 'Reference number',
          },
        ];
      case AdminModuleType.parcels:
        return [
          {
            'key': 'flat',
            'label': 'Flat ID *',
            'number': true,
          },
          {
            'key': 'recipient_name',
            'label': 'Recipient name *',
          },
          {'key': 'courier_name', 'label': 'Courier name'},
          {
            'key': 'tracking_number',
            'label': 'Tracking number',
          },
        ];
      case AdminModuleType.vehicles:
        return [
          {
            'key': 'flat',
            'label': 'Flat ID *',
            'number': true,
          },
          {'key': 'owner_name', 'label': 'Owner name *'},
          {
            'key': 'vehicle_number',
            'label': 'Vehicle number *',
          },
          {
            'key': 'vehicle_type',
            'label': 'Type (CAR/BIKE/OTHER) *',
          },
          {
            'key': 'parking_slot',
            'label': 'Parking slot',
          },
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.domesticWorkers:
        return [
          {'key': 'name', 'label': 'Worker name *'},
          {
            'key': 'service_type',
            'label': 'Service type *',
          },
          {'key': 'phone', 'label': 'Phone'},
          {'key': 'id_number', 'label': 'ID number'},
          {
            'key': 'police_verified',
            'label': 'Police verified',
            'bool': true,
          },
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.events:
        return [
          {'key': 'title', 'label': 'Title *'},
          {
            'key': 'event_date',
            'label':
                'Event date/time (YYYY-MM-DDTHH:MM:SS) *',
          },
          {'key': 'venue', 'label': 'Venue *'},
          {
            'key': 'description',
            'label': 'Description',
            'lines': 3,
          },
          {
            'key': 'registration_required',
            'label': 'Registration required',
            'bool': true,
          },
          {
            'key': 'contribution_amount',
            'label': 'Contribution amount',
            'decimal': true,
          },
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.meetings:
        return [
          {'key': 'title', 'label': 'Title *'},
          {
            'key': 'meeting_date',
            'label':
                'Meeting date/time (YYYY-MM-DDTHH:MM:SS) *',
          },
          {'key': 'venue', 'label': 'Venue *'},
          {'key': 'agenda', 'label': 'Agenda', 'lines': 3},
          {
            'key': 'minutes',
            'label': 'Minutes',
            'lines': 3,
          },
        ];
      case AdminModuleType.assets:
        return [
          {'key': 'name', 'label': 'Asset name *'},
          {'key': 'category', 'label': 'Category'},
          {'key': 'asset_code', 'label': 'Asset code'},
          {'key': 'location', 'label': 'Location'},
          {
            'key': 'purchase_date',
            'label': 'Purchase date (YYYY-MM-DD)',
          },
          {
            'key': 'warranty_until',
            'label': 'Warranty until (YYYY-MM-DD)',
          },
          {
            'key': 'next_service_date',
            'label': 'Next service date (YYYY-MM-DD)',
          },
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.vendorAmc:
        return [
          {
            'key': 'service_name',
            'label': 'Service name *',
          },
          {'key': 'vendor_name', 'label': 'Vendor name *'},
          {
            'key': 'contact_person',
            'label': 'Contact person',
          },
          {'key': 'phone', 'label': 'Phone'},
          {
            'key': 'amount',
            'label': 'Amount',
            'decimal': true,
          },
          {
            'key': 'start_date',
            'label': 'Start date (YYYY-MM-DD)',
          },
          {
            'key': 'renewal_date',
            'label': 'Renewal date (YYYY-MM-DD)',
          },
          {'key': 'notes', 'label': 'Notes', 'lines': 3},
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.expenses:
        return [
          {'key': 'title', 'label': 'Title *'},
          {'key': 'category', 'label': 'Category *'},
          {
            'key': 'amount',
            'label': 'Amount *',
            'decimal': true,
          },
          {
            'key': 'expense_date',
            'label': 'Expense date (YYYY-MM-DD) *',
          },
          {'key': 'vendor', 'label': 'Vendor'},
          {'key': 'notes', 'label': 'Notes', 'lines': 3},
        ];
      case AdminModuleType.emergencyContacts:
        return [
          {'key': 'name', 'label': 'Name *'},
          {'key': 'category', 'label': 'Category *'},
          {'key': 'phone', 'label': 'Phone *'},
          {
            'key': 'secondary_phone',
            'label': 'Secondary phone',
          },
          {'key': 'notes', 'label': 'Notes', 'lines': 3},
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      case AdminModuleType.polls:
        return [
          {'key': 'question', 'label': 'Question *'},
          {
            'key': 'description',
            'label': 'Description',
            'lines': 3,
          },
          {
            'key': 'closes_at',
            'label':
                'Closes at (YYYY-MM-DDTHH:MM:SS)',
          },
          {
            'key': 'options',
            'label':
                'Options separated by commas (minimum 2) *',
          },
          {
            'key': 'is_active',
            'label': 'Active',
            'bool': true,
            'default': true,
          },
        ];
      default:
        return [];
    }
  }

  Future<void> _showCreateDialog() async {
    final fields = _formFields();

    if (fields.isEmpty) {
      _showMessage(
        'Create action is not available for $_title.',
      );
      return;
    }

    final controllers =
        <String, TextEditingController>{};
    final boolValues = <String, bool>{};

    for (final field in fields) {
      final key = field['key'] as String;

      if (field['bool'] == true) {
        boolValues[key] =
            field['default'] == true;
      } else {
        controllers[key] = TextEditingController();
      }
    }

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (
            context,
            setDialogState,
          ) {
            return AlertDialog(
              title: Text('Add $_title'),
              content: SizedBox(
                width: 520,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: fields.map((field) {
                      final key = field['key'] as String;
                      final label =
                          field['label'] as String;

                      if (field['bool'] == true) {
                        return SwitchListTile(
                          contentPadding: EdgeInsets.zero,
                          title: Text(label),
                          value: boolValues[key] ?? false,
                          onChanged: (value) {
                            setDialogState(() {
                              boolValues[key] = value;
                            });
                          },
                        );
                      }

                      return Padding(
                        padding:
                            const EdgeInsets.only(bottom: 10),
                        child: TextField(
                          controller: controllers[key],
                          maxLines:
                              field['lines'] as int? ?? 1,
                          keyboardType:
                              field['number'] == true ||
                                      field['decimal'] ==
                                          true
                                  ? const TextInputType
                                      .numberWithOptions(
                                      decimal: true,
                                    )
                                  : TextInputType.text,
                          decoration: InputDecoration(
                            labelText: label,
                            border:
                                const OutlineInputBorder(),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () =>
                      Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: _isSubmitting
                      ? null
                      : () async {
                          final body =
                              <String, dynamic>{};

                          for (final field in fields) {
                            final key =
                                field['key'] as String;

                            if (field['bool'] == true) {
                              body[key] =
                                  boolValues[key] ?? false;
                              continue;
                            }

                            final raw =
                                controllers[key]!.text.trim();

                            if (raw.isEmpty) {
                              continue;
                            }

                            if (key == 'options') {
                              body[key] = raw
                                  .split(',')
                                  .map((e) => e.trim())
                                  .where(
                                    (e) => e.isNotEmpty,
                                  )
                                  .toList();
                            } else if (field['number'] ==
                                true) {
                              body[key] =
                                  int.tryParse(raw) ?? raw;
                            } else if (field['decimal'] ==
                                true) {
                              body[key] =
                                  double.tryParse(raw) ??
                                      raw;
                            } else {
                              body[key] = raw;
                            }
                          }

                          final success = await _request(
                            method: 'POST',
                            endpoint: _endpoint,
                            body: body,
                          );

                          // Close the dialog only after the async request
                          // has completed. This avoids disposing inherited
                          // widgets while the request rebuilds the page.
                          if (success && dialogContext.mounted) {
                            Navigator.pop(dialogContext);
                          }
                        },
                  child: const Text('Save'),
                ),
              ],
            );
          },
        );
      },
    );

    for (final controller in controllers.values) {
      controller.dispose();
    }
  }

  // Modules that support PATCH editing from the Admin app.
  bool get _canEdit {
    return {
      AdminModuleType.flats,
      AdminModuleType.residents,
      AdminModuleType.lostFound,
      AdminModuleType.notices,
      AdminModuleType.visitors,
      AdminModuleType.invoices,
      AdminModuleType.parcels,
      AdminModuleType.vehicles,
      AdminModuleType.domesticWorkers,
      AdminModuleType.events,
      AdminModuleType.meetings,
      AdminModuleType.assets,
      AdminModuleType.vendorAmc,
      AdminModuleType.expenses,
      AdminModuleType.emergencyContacts,
      AdminModuleType.polls,
    }.contains(widget.module);
  }

  // Opens the same field definition used by Create, but pre-fills
  // the current values and sends a PATCH request.
  Future<void> _showEditDialog(
    Map<String, dynamic> item,
  ) async {
    final fields = _formFields();
    final id = item['id'];

    if (fields.isEmpty || id == null) {
      _showMessage('Edit action is not available for $_title.');
      return;
    }

    final controllers = <String, TextEditingController>{};
    final boolValues = <String, bool>{};

    for (final field in fields) {
      final key = field['key'] as String;

      // Password is optional while editing a resident.
      if (widget.module == AdminModuleType.residents &&
          key == 'password') {
        controllers[key] = TextEditingController();
        continue;
      }

      if (field['bool'] == true) {
        boolValues[key] = item[key] == true;
      } else {
        dynamic value = item[key];

        // Poll options are returned as objects/lists.
        if (key == 'options' && value is List) {
          value = value.map((option) {
            if (option is Map && option['label'] != null) {
              return option['label'].toString();
            }
            return option.toString();
          }).join(', ');
        }

        controllers[key] = TextEditingController(
          text: value == null ? '' : value.toString(),
        );
      }
    }

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (
            context,
            setDialogState,
          ) {
            return AlertDialog(
              title: Text('Edit $_title'),
              content: SizedBox(
                width: 520,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: fields.map((field) {
                      final key = field['key'] as String;
                      final label = field['label'] as String;

                      if (field['bool'] == true) {
                        return SwitchListTile(
                          contentPadding: EdgeInsets.zero,
                          title: Text(label),
                          value: boolValues[key] ?? false,
                          onChanged: (value) {
                            setDialogState(() {
                              boolValues[key] = value;
                            });
                          },
                        );
                      }

                      return Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: TextField(
                          controller: controllers[key],
                          maxLines: field['lines'] as int? ?? 1,
                          obscureText:
                              widget.module == AdminModuleType.residents &&
                                  key == 'password',
                          keyboardType:
                              field['number'] == true ||
                                      field['decimal'] == true
                                  ? const TextInputType.numberWithOptions(
                                      decimal: true,
                                    )
                                  : TextInputType.text,
                          decoration: InputDecoration(
                            labelText:
                                widget.module == AdminModuleType.residents &&
                                        key == 'password'
                                    ? 'New password (leave blank to keep current)'
                                    : label,
                            border: const OutlineInputBorder(),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: _isSubmitting
                      ? null
                      : () async {
                          final body = <String, dynamic>{};

                          for (final field in fields) {
                            final key = field['key'] as String;

                            if (field['bool'] == true) {
                              body[key] = boolValues[key] ?? false;
                              continue;
                            }

                            final raw = controllers[key]!.text.trim();

                            // Blank password means do not change it.
                            if (widget.module ==
                                    AdminModuleType.residents &&
                                key == 'password' &&
                                raw.isEmpty) {
                              continue;
                            }

                            if (raw.isEmpty) {
                              body[key] = '';
                              continue;
                            }

                            if (key == 'options') {
                              body[key] = raw
                                  .split(',')
                                  .map((e) => e.trim())
                                  .where((e) => e.isNotEmpty)
                                  .toList();
                            } else if (field['number'] == true) {
                              body[key] = int.tryParse(raw) ?? raw;
                            } else if (field['decimal'] == true) {
                              body[key] = double.tryParse(raw) ?? raw;
                            } else {
                              body[key] = raw;
                            }
                          }

                          final success = await _request(
                            method: 'PATCH',
                            endpoint: '$_endpoint$id/',
                            body: body,
                          );

                          if (success && dialogContext.mounted) {
                            Navigator.pop(dialogContext);
                          }
                        },
                  child: const Text('Save Changes'),
                ),
              ],
            );
          },
        );
      },
    );

    for (final controller in controllers.values) {
      controller.dispose();
    }
  }

  List<String> _statusOptions(
    Map<String, dynamic> item,
  ) {
    switch (widget.module) {
      case AdminModuleType.lostFound:
        return ['OPEN', 'CLAIMED', 'CLOSED'];
      case AdminModuleType.complaints:
        return [
          'OPEN',
          'IN_PROGRESS',
          'RESOLVED',
          'CLOSED',
        ];
      case AdminModuleType.visitors:
        return [
          'PENDING',
          'APPROVED',
          'DENIED',
          'CHECKED_IN',
          'CHECKED_OUT',
        ];
      case AdminModuleType.parcels:
        return [
          'RECEIVED',
          'NOTIFIED',
          'COLLECTED',
        ];
      case AdminModuleType.amenityBookings:
        return [
          'REQUESTED',
          'CONFIRMED',
          'COMPLETED',
          'CANCELLED',
        ];
      case AdminModuleType.certificates:
        return [
          'PENDING',
          'APPROVED',
          'REJECTED',
          'ISSUED',
        ];
      case AdminModuleType.moveRequests:
        return [
          'REQUESTED',
          'APPROVED',
          'COMPLETED',
          'REJECTED',
        ];
      default:
        return [];
    }
  }

  Future<void> _showStatusDialog(
    Map<String, dynamic> item,
  ) async {
    final options = _statusOptions(item);

    if (options.isEmpty) return;

    String selected =
        item['status']?.toString() ?? options.first;

    if (!options.contains(selected)) {
      selected = options.first;
    }

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (
            context,
            setDialogState,
          ) {
            return AlertDialog(
              title: Text('Update $_title Status'),
              content: DropdownButtonFormField<String>(
                initialValue: selected,
                decoration: const InputDecoration(
                  labelText: 'Status',
                  border: OutlineInputBorder(),
                ),
                items: options
                    .map(
                      (status) =>
                          DropdownMenuItem<String>(
                        value: status,
                        child: Text(status),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  if (value != null) {
                    setDialogState(() {
                      selected = value;
                    });
                  }
                },
              ),
              actions: [
                TextButton(
                  onPressed: () =>
                      Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    final id = item['id'];
                    if (id == null) return;

                    final success = await _request(
                      method: 'PATCH',
                      endpoint: '$_endpoint$id/',
                      body: {'status': selected},
                    );

                    if (success && dialogContext.mounted) {
                      Navigator.pop(dialogContext);
                    }
                  },
                  child: const Text('Update'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _toggleActive(
    Map<String, dynamic> item,
  ) async {
    final current = item['is_active'] == true;
    await _patchItem(
      item,
      {'is_active': !current},
    );
  }

  Future<void> _recordPaymentForInvoice(
    Map<String, dynamic> invoice,
  ) async {
    final invoiceId = invoice['id'];
    if (invoiceId == null) return;

    final amount = TextEditingController();
    final method = TextEditingController(text: 'UPI');
    final reference = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Record Payment'),
          content: SizedBox(
            width: 420,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'Invoice #$invoiceId • '
                  '${invoice['flat_name'] ?? ''}',
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: amount,
                  keyboardType:
                      const TextInputType.numberWithOptions(
                    decimal: true,
                  ),
                  decoration: const InputDecoration(
                    labelText: 'Amount *',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: method,
                  decoration: const InputDecoration(
                    labelText:
                        'Method (CASH/UPI/BANK/OTHER) *',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 10),
                TextField(
                  controller: reference,
                  decoration: const InputDecoration(
                    labelText: 'Reference number',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () =>
                  Navigator.pop(dialogContext),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () async {
                final parsed =
                    double.tryParse(amount.text.trim());

                if (parsed == null || parsed <= 0) {
                  _showMessage(
                    'Enter a valid payment amount.',
                  );
                  return;
                }

                final body = <String, dynamic>{
                  'invoice': invoiceId,
                  'amount': parsed,
                  'method': method.text.trim(),
                };

                if (reference.text.trim().isNotEmpty) {
                  body['reference_number'] =
                      reference.text.trim();
                }

                final success = await _request(
                  method: 'POST',
                  endpoint: 'billing/payments/',
                  body: body,
                );

                if (success && dialogContext.mounted) {
                  Navigator.pop(dialogContext);
                }
              },
              child: const Text('Record'),
            ),
          ],
        );
      },
    );

    amount.dispose();
    method.dispose();
    reference.dispose();
  }

  String _value(dynamic value) {
    if (value == null) return '-';
    if (value is bool) return value ? 'Yes' : 'No';
    if (value is List) {
      return value.map((e) => e.toString()).join(', ');
    }
    final text = value.toString().trim();
    return text.isEmpty ? '-' : text;
  }

  List<dynamic> get _filteredItems {
    if (_search.trim().isEmpty) {
      return _items;
    }

    final query = _search.toLowerCase().trim();

    return _items.where((raw) {
      if (raw is! Map) return false;
      final item = Map<String, dynamic>.from(raw);
      final haystack = item.values
          .map((value) => value?.toString() ?? '')
          .join(' ')
          .toLowerCase();
      return haystack.contains(query);
    }).toList();
  }

  String _itemTitle(
    Map<String, dynamic> item,
    int index,
  ) {
    for (final key in [
      'flat_number',
      'username',
      'title',
      'name',
      'question',
      'service_name',
      'vehicle_number',
      'recipient_name',
      'worker_name',
      'invoice_title',
      'request_type',
      'owner_name',
    ]) {
      final value = item[key];
      if (value != null &&
          value.toString().trim().isNotEmpty) {
        return value.toString();
      }
    }

    return '$_title ${index + 1}';
  }

  String _itemSubtitle(
    Map<String, dynamic> item,
  ) {
    final parts = <String>[];

    for (final key in [
      'building_name',
      'flat_name',
      'first_name',
      'item_type',
      'status',
      'category',
      'vendor_name',
      'amount',
      'event_date',
      'meeting_date',
      'phone',
    ]) {
      final value = item[key];
      if (value != null &&
          value.toString().trim().isNotEmpty) {
        parts.add(value.toString());
      }

      if (parts.length == 2) break;
    }

    return parts.join(' • ');
  }

  bool get _hasActiveToggle {
    return {
      AdminModuleType.residents,
      AdminModuleType.vehicles,
      AdminModuleType.domesticWorkers,
      AdminModuleType.assets,
      AdminModuleType.vendorAmc,
      AdminModuleType.emergencyContacts,
      AdminModuleType.polls,
    }.contains(widget.module);
  }

  Widget _itemActions(
    Map<String, dynamic> item,
  ) {
    final actions = <Widget>[];

    if (_canEdit) {
      actions.add(
        OutlinedButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _showEditDialog(item),
          icon: const Icon(Icons.edit),
          label: const Text('Edit'),
        ),
      );
    }

    if (_statusOptions(item).isNotEmpty) {
      actions.add(
        OutlinedButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _showStatusDialog(item),
          icon: const Icon(Icons.sync),
          label: const Text('Update Status'),
        ),
      );
    }

    if (_hasActiveToggle &&
        item.containsKey('is_active')) {
      actions.add(
        OutlinedButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _toggleActive(item),
          icon: Icon(
            item['is_active'] == true
                ? Icons.pause_circle
                : Icons.play_circle,
          ),
          label: Text(
            item['is_active'] == true
                ? 'Deactivate'
                : 'Activate',
          ),
        ),
      );
    }

    if (widget.module ==
        AdminModuleType.invoices) {
      final status =
          item['status']?.toString() ?? '';

      if (status != 'PAID') {
        actions.add(
          FilledButton.icon(
            onPressed: _isSubmitting
                ? null
                : () =>
                    _recordPaymentForInvoice(item),
            icon: const Icon(Icons.payments),
            label: const Text('Record Payment'),
          ),
        );
      }
    }

    if (actions.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: actions,
      ),
    );
  }

  Widget _details(
    Map<String, dynamic> item,
  ) {
    final entries = item.entries.where((entry) {
      return entry.key != 'options';
    }).toList();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ...entries.map(
          (entry) => Padding(
            padding:
                const EdgeInsets.only(bottom: 6),
            child: Row(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 150,
                  child: Text(
                    '${entry.key.replaceAll('_', ' ')}:',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Expanded(
                  child: Text(_value(entry.value)),
                ),
              ],
            ),
          ),
        ),
        if (item['options'] is List) ...[
          const SizedBox(height: 6),
          const Text(
            'Poll Options:',
            style: TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          ...(item['options'] as List).map(
            (option) => Text(
              option is Map
                  ? '• ${option['label'] ?? ''} '
                      '(${option['vote_count'] ?? 0} votes)'
                  : '• $option',
            ),
          ),
        ],
        _itemActions(item),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filteredItems;

    return Scaffold(
      appBar: AppBar(
        title: Text(_title),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadItems,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton: _canCreate
          ? FloatingActionButton.extended(
              onPressed: _isSubmitting
                  ? null
                  : _showCreateDialog,
              icon: const Icon(Icons.add),
              label: Text('Add $_title'),
            )
          : null,
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _error != null
              ? Center(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment:
                          MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 50,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _error!,
                          textAlign:
                              TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: _loadItems,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : Column(
                  children: [
                    Padding(
                      padding:
                          const EdgeInsets.all(16),
                      child: TextField(
                        decoration:
                            InputDecoration(
                          prefixIcon:
                              const Icon(Icons.search),
                          hintText: 'Search $_title',
                          border:
                              const OutlineInputBorder(),
                        ),
                        onChanged: (value) {
                          setState(() {
                            _search = value;
                          });
                        },
                      ),
                    ),
                    Expanded(
                      child: RefreshIndicator(
                        onRefresh: _loadItems,
                        child: filtered.isEmpty
                            ? ListView(
                                physics:
                                    const AlwaysScrollableScrollPhysics(),
                                children: [
                                  SizedBox(
                                    height: 420,
                                    child: Center(
                                      child: Text(
                                        'No $_title records found.',
                                      ),
                                    ),
                                  ),
                                ],
                              )
                            : ListView.builder(
                                padding:
                                    const EdgeInsets.fromLTRB(
                                  16,
                                  0,
                                  16,
                                  100,
                                ),
                                itemCount:
                                    filtered.length,
                                itemBuilder:
                                    (context, index) {
                                  final raw =
                                      filtered[index];

                                  if (raw is! Map) {
                                    return const SizedBox
                                        .shrink();
                                  }

                                  final item =
                                      Map<String, dynamic>
                                          .from(raw);

                                  return Card(
                                    margin:
                                        const EdgeInsets.only(
                                      bottom: 12,
                                    ),
                                    child:
                                        ExpansionTile(
                                      leading:
                                          CircleAvatar(
                                        child:
                                            Icon(_icon),
                                      ),
                                      title: Text(
                                        _itemTitle(
                                          item,
                                          index,
                                        ),
                                        style:
                                            const TextStyle(
                                          fontWeight:
                                              FontWeight
                                                  .bold,
                                        ),
                                      ),
                                      subtitle: Text(
                                        _itemSubtitle(
                                          item,
                                        ),
                                      ),
                                      children: [
                                        Padding(
                                          padding:
                                              const EdgeInsets
                                                  .fromLTRB(
                                            16,
                                            0,
                                            16,
                                            16,
                                          ),
                                          child: _details(
                                            item,
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                      ),
                    ),
                  ],
                ),
    );
  }
}

class SecurityDashboardScreen extends StatefulWidget {
  final String username;

  const SecurityDashboardScreen({
    super.key,
    required this.username,
  });

  @override
  State<SecurityDashboardScreen> createState() =>
      _SecurityDashboardScreenState();
}

class _SecurityDashboardScreenState
    extends State<SecurityDashboardScreen> {
  final _storage = const FlutterSecureStorage();

  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  String? _error;

  Map<String, dynamic>? _dashboard;
  List<dynamic> _recentVisitors = [];
  List<dynamic> _recentParcels = [];

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'access_token');

      if (token == null) {
        setState(() {
          _error = 'Login token not found.';
          _isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/dashboard/security/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 &&
          data['success'] == true) {
        setState(() {
          _dashboard =
              Map<String, dynamic>.from(data['dashboard']);
          _recentVisitors =
              data['recent_visitors'] ?? [];
          _recentParcels =
              data['recent_parcels'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error =
              data['message'] ?? 'Unable to load dashboard.';
          _isLoading = false;
        });
      }
    } catch (_) {
      setState(() {
        _error = 'Unable to connect to the server.';
        _isLoading = false;
      });
    }
  }

  Future<void> _logout() async {
    await _storage.deleteAll();

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => const LoginScreen(),
      ),
      (route) => false,
    );
  }

  // Responsive Security dashboard card.
  Widget _actionCard({
    required String title,
    required String value,
    required IconData icon,
    required SecurityModuleType module,
  }) {
    return Card(
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () async {
          await Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => SecurityModuleScreen(
                module: module,
              ),
            ),
          );
          if (mounted) {
            _loadDashboard();
          }
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: 10,
            vertical: 12,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 30),
              const SizedBox(height: 7),
              FittedBox(
                fit: BoxFit.scaleDown,
                child: Text(
                  value,
                  maxLines: 1,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(height: 5),
              Text(
                title,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 13,
                  height: 1.15,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _openModule(SecurityModuleType module) async {
    await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => SecurityModuleScreen(
          module: module,
        ),
      ),
    );
    if (mounted) {
      _loadDashboard();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Security Dashboard'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadDashboard,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Logout',
            onPressed: _logout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment:
                        MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 50,
                      ),
                      const SizedBox(height: 12),
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _loadDashboard,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadDashboard,
                  child: ListView(
                    padding: const EdgeInsets.all(20),
                    children: [
                      Text(
                        'Welcome, ${widget.username}',
                        style: Theme.of(context)
                            .textTheme
                            .headlineSmall
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 6),
                      const Text('Role: SECURITY'),
                      const SizedBox(height: 24),
                      Text(
                        'Overview',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 12),
                      GridView.count(
                        crossAxisCount:
                            MediaQuery.of(context).size.width >
                                    700
                                ? 4
                                : 2,
                        shrinkWrap: true,
                        physics:
                            const NeverScrollableScrollPhysics(),
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 1.0,
                        children: [
                          _actionCard(
                            title: 'Visitors Today',
                            value:
                                '${_dashboard?['visitors_today'] ?? 0}',
                            icon: Icons.people,
                            module:
                                SecurityModuleType.visitors,
                          ),
                          _actionCard(
                            title: 'Pending Visitors',
                            value:
                                '${_dashboard?['pending_visitors'] ?? 0}',
                            icon: Icons.hourglass_empty,
                            module:
                                SecurityModuleType.visitors,
                          ),
                          _actionCard(
                            title: 'Checked In',
                            value:
                                '${_dashboard?['checked_in_visitors'] ?? 0}',
                            icon: Icons.login,
                            module:
                                SecurityModuleType.visitors,
                          ),
                          _actionCard(
                            title: 'Parcels Waiting',
                            value:
                                '${_dashboard?['parcels_waiting'] ?? 0}',
                            icon: Icons.inventory_2,
                            module:
                                SecurityModuleType.parcels,
                          ),
                          _actionCard(
                            title: 'Workers Active',
                            value:
                                '${_dashboard?['active_domestic_workers'] ?? 0}',
                            icon: Icons.badge,
                            module:
                                SecurityModuleType.workers,
                          ),
                          _actionCard(
                            title: 'Staff Inside',
                            value:
                                '${_dashboard?['staff_inside'] ?? 0}',
                            icon: Icons.how_to_reg,
                            module:
                                SecurityModuleType.attendance,
                          ),
                          _actionCard(
                            title: 'Active Vehicles',
                            value:
                                '${_dashboard?['active_vehicles'] ?? 0}',
                            icon: Icons.directions_car,
                            module:
                                SecurityModuleType.vehicles,
                          ),
                        ],
                      ),
                      const SizedBox(height: 28),
                      Text(
                        'Recent Visitors',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 10),
                      if (_recentVisitors.isEmpty)
                        const Card(
                          child: Padding(
                            padding: EdgeInsets.all(18),
                            child: Text(
                              'No recent visitors.',
                            ),
                          ),
                        )
                      else
                        ..._recentVisitors.map(
                          (visitor) => Card(
                            child: ListTile(
                              leading:
                                  const Icon(Icons.person),
                              title: Text(
                                visitor['name'] ?? '',
                              ),
                              subtitle: Text(
                                '${visitor['flat'] ?? ''} • ${visitor['status'] ?? ''}',
                              ),
                              trailing: const Icon(
                                Icons.chevron_right,
                              ),
                              onTap: () => _openModule(
                                SecurityModuleType.visitors,
                              ),
                            ),
                          ),
                        ),
                      const SizedBox(height: 28),
                      Text(
                        'Recent Parcels',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                      const SizedBox(height: 10),
                      if (_recentParcels.isEmpty)
                        const Card(
                          child: Padding(
                            padding: EdgeInsets.all(18),
                            child: Text(
                              'No recent parcels.',
                            ),
                          ),
                        )
                      else
                        ..._recentParcels.map(
                          (parcel) => Card(
                            child: ListTile(
                              leading: const Icon(
                                Icons.inventory,
                              ),
                              title: Text(
                                parcel['recipient_name'] ??
                                    '',
                              ),
                              subtitle: Text(
                                '${parcel['courier_name'] ?? ''} • ${parcel['status'] ?? ''}',
                              ),
                              trailing: const Icon(
                                Icons.chevron_right,
                              ),
                              onTap: () => _openModule(
                                SecurityModuleType.parcels,
                              ),
                            ),
                          ),
                        ),
                      const SizedBox(height: 30),
                    ],
                  ),
                ),
    );
  }
}

enum SecurityModuleType {
  visitors,
  parcels,
  workers,
  attendance,
  vehicles,
}

class SecurityModuleScreen extends StatefulWidget {
  final SecurityModuleType module;

  const SecurityModuleScreen({
    super.key,
    required this.module,
  });

  @override
  State<SecurityModuleScreen> createState() =>
      _SecurityModuleScreenState();
}

class _SecurityModuleScreenState
    extends State<SecurityModuleScreen> {
  final _storage = const FlutterSecureStorage();
  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _error;
  List<dynamic> _items = [];
  String _search = '';

  String get _title {
    switch (widget.module) {
      case SecurityModuleType.visitors:
        return 'Visitor Management';
      case SecurityModuleType.parcels:
        return 'Parcel Management';
      case SecurityModuleType.workers:
        return 'Domestic Workers';
      case SecurityModuleType.attendance:
        return 'Worker Attendance';
      case SecurityModuleType.vehicles:
        return 'Vehicle Lookup';
    }
  }

  String get _endpoint {
    switch (widget.module) {
      case SecurityModuleType.visitors:
        return 'visitors/';
      case SecurityModuleType.parcels:
        return 'parcels/';
      case SecurityModuleType.workers:
        return 'domestic-workers/';
      case SecurityModuleType.attendance:
        return 'domestic-workers/attendance/';
      case SecurityModuleType.vehicles:
        return 'vehicles/';
    }
  }

  String get _responseKey {
    switch (widget.module) {
      case SecurityModuleType.visitors:
        return 'visitors';
      case SecurityModuleType.parcels:
        return 'parcels';
      case SecurityModuleType.workers:
        return 'workers';
      case SecurityModuleType.attendance:
        return 'attendance';
      case SecurityModuleType.vehicles:
        return 'vehicles';
    }
  }

  IconData get _icon {
    switch (widget.module) {
      case SecurityModuleType.visitors:
        return Icons.people;
      case SecurityModuleType.parcels:
        return Icons.inventory_2;
      case SecurityModuleType.workers:
        return Icons.badge;
      case SecurityModuleType.attendance:
        return Icons.how_to_reg;
      case SecurityModuleType.vehicles:
        return Icons.directions_car;
    }
  }

  bool get _showSearch {
    return widget.module != SecurityModuleType.attendance;
  }

  bool get _showCheckInButton {
    return widget.module == SecurityModuleType.attendance;
  }

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<String?> _token() {
    return _storage.read(key: 'access_token');
  }

  Map<String, String> _headers(String token) {
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  Future<void> _loadItems() async {
    if (mounted) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      final token = await _token();

      if (token == null) {
        if (mounted) {
          setState(() {
            _error = 'Login token not found.';
            _isLoading = false;
          });
        }
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/$_endpoint'),
        headers: _headers(token),
      );

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200) {
        List<dynamic> items = [];

        if (data is Map<String, dynamic>) {
          final preferred = data[_responseKey];
          if (preferred is List) {
            items = preferred;
          }
        } else if (data is List) {
          items = data;
        }

        if (mounted) {
          setState(() {
            _items = items;
            _isLoading = false;
          });
        }
      } else {
        final message = _messageFromData(
          data,
          'Unable to load $_title.',
        );

        if (mounted) {
          setState(() {
            _error =
                '$message (HTTP ${response.statusCode})';
            _isLoading = false;
          });
        }
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _error = 'Unable to connect to the server.';
          _isLoading = false;
        });
      }
    }
  }

  String _messageFromData(
    dynamic data,
    String fallback,
  ) {
    if (data is Map<String, dynamic>) {
      if (data['message'] != null) {
        return data['message'].toString();
      }
      if (data['detail'] != null) {
        return data['detail'].toString();
      }
      if (data['errors'] != null) {
        return data['errors'].toString();
      }
    }
    return fallback;
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<bool> _patch(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    if (_isSubmitting) return false;

    setState(() => _isSubmitting = true);

    try {
      final token = await _token();
      if (token == null) {
        _showMessage('Login token not found.');
        return false;
      }

      final response = await http.patch(
        Uri.parse('$baseUrl/$endpoint'),
        headers: _headers(token),
        body: jsonEncode(body),
      );

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200) {
        _showMessage(
          data is Map<String, dynamic> &&
                  data['message'] != null
              ? data['message'].toString()
              : 'Updated successfully.',
        );
        await _loadItems();
        return true;
      }

      _showMessage(
        _messageFromData(
          data,
          'Update failed (HTTP ${response.statusCode}).',
        ),
      );
      return false;
    } catch (_) {
      _showMessage('Unable to connect to the server.');
      return false;
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  Future<bool> _post(
    String endpoint,
    Map<String, dynamic> body,
  ) async {
    if (_isSubmitting) return false;

    setState(() => _isSubmitting = true);

    try {
      final token = await _token();
      if (token == null) {
        _showMessage('Login token not found.');
        return false;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/$endpoint'),
        headers: _headers(token),
        body: jsonEncode(body),
      );

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200 ||
          response.statusCode == 201) {
        _showMessage(
          data is Map<String, dynamic> &&
                  data['message'] != null
              ? data['message'].toString()
              : 'Saved successfully.',
        );
        await _loadItems();
        return true;
      }

      _showMessage(
        _messageFromData(
          data,
          'Request failed (HTTP ${response.statusCode}).',
        ),
      );
      return false;
    } catch (_) {
      _showMessage('Unable to connect to the server.');
      return false;
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  String _value(dynamic value) {
    if (value == null) return '-';
    if (value is bool) {
      return value ? 'Yes' : 'No';
    }
    final text = value.toString().trim();
    return text.isEmpty ? '-' : text;
  }

  String _itemSearchText(Map<String, dynamic> item) {
    return item.values
        .map((value) => value?.toString() ?? '')
        .join(' ')
        .toLowerCase();
  }

  List<dynamic> get _filteredItems {
    if (_search.trim().isEmpty) {
      return _items;
    }

    final query = _search.toLowerCase().trim();

    return _items.where((raw) {
      if (raw is! Map) return false;
      final item = Map<String, dynamic>.from(raw);
      return _itemSearchText(item).contains(query);
    }).toList();
  }

  Future<void> _setVisitorStatus(
    Map<String, dynamic> visitor,
    String status,
  ) async {
    final id = visitor['id'];
    if (id == null) return;

    await _patch(
      'visitors/$id/',
      {'status': status},
    );
  }

  Future<void> _setParcelStatus(
    Map<String, dynamic> parcel,
    String status,
  ) async {
    final id = parcel['id'];
    if (id == null) return;

    await _patch(
      'parcels/$id/',
      {'status': status},
    );
  }

  Future<List<Map<String, dynamic>>> _loadWorkers()
      async {
    final token = await _token();
    if (token == null) return [];

    final response = await http.get(
      Uri.parse('$baseUrl/domestic-workers/'),
      headers: _headers(token),
    );

    if (response.statusCode != 200) return [];

    final data = jsonDecode(response.body);

    if (data is! Map<String, dynamic> ||
        data['workers'] is! List) {
      return [];
    }

    return (data['workers'] as List)
        .whereType<Map>()
        .map(
          (item) => Map<String, dynamic>.from(item),
        )
        .toList();
  }

  Future<void> _showWorkerCheckInDialog() async {
    List<Map<String, dynamic>> workers = [];

    try {
      workers = await _loadWorkers();
    } catch (_) {
      _showMessage('Unable to load workers.');
      return;
    }

    workers = workers
        .where((worker) => worker['is_active'] != false)
        .toList();

    if (workers.isEmpty) {
      _showMessage('No active workers found.');
      return;
    }

    int? workerId = workers.first['id'] as int?;
    final gateNote = TextEditingController();

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (
            context,
            setDialogState,
          ) {
            return AlertDialog(
              title: const Text('Worker Check In'),
              content: SizedBox(
                width: 430,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<int>(
                      initialValue: workerId,
                      decoration: const InputDecoration(
                        labelText: 'Worker *',
                      ),
                      items: workers
                          .map(
                            (worker) =>
                                DropdownMenuItem<int>(
                              value:
                                  worker['id'] as int?,
                              child: Text(
                                '${worker['name'] ?? 'Worker'}'
                                ' (${worker['service_type'] ?? ''})',
                              ),
                            ),
                          )
                          .toList(),
                      onChanged: (value) {
                        setDialogState(() {
                          workerId = value;
                        });
                      },
                    ),
                    TextField(
                      controller: gateNote,
                      maxLines: 2,
                      decoration: const InputDecoration(
                        labelText:
                            'Gate note (optional)',
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () =>
                      Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    if (workerId == null) {
                      _showMessage(
                        'Please select a worker.',
                      );
                      return;
                    }

                    final success = await _post(
                      'domestic-workers/attendance/',
                      {
                        'worker': workerId,
                        'gate_note':
                            gateNote.text.trim(),
                      },
                    );

                    if (success && dialogContext.mounted) {
                      Navigator.pop(dialogContext);
                    }
                  },
                  child: const Text('Check In'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _checkOutAttendance(
    Map<String, dynamic> attendance,
  ) async {
    final id = attendance['id'];
    if (id == null) return;

    await _patch(
      'domestic-workers/attendance/$id/',
      {},
    );
  }

  Widget _visitorActions(
    Map<String, dynamic> visitor,
  ) {
    final status =
        visitor['status']?.toString() ?? '';

    final actions = <Widget>[];

    if (status == 'PENDING') {
      actions.addAll([
        FilledButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _setVisitorStatus(
                    visitor,
                    'APPROVED',
                  ),
          icon: const Icon(Icons.check),
          label: const Text('Approve'),
        ),
        OutlinedButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _setVisitorStatus(
                    visitor,
                    'DENIED',
                  ),
          icon: const Icon(Icons.close),
          label: const Text('Deny'),
        ),
      ]);
    } else if (status == 'APPROVED') {
      actions.add(
        FilledButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _setVisitorStatus(
                    visitor,
                    'CHECKED_IN',
                  ),
          icon: const Icon(Icons.login),
          label: const Text('Check In'),
        ),
      );
    } else if (status == 'CHECKED_IN') {
      actions.add(
        FilledButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _setVisitorStatus(
                    visitor,
                    'CHECKED_OUT',
                  ),
          icon: const Icon(Icons.logout),
          label: const Text('Check Out'),
        ),
      );
    }

    if (actions.isEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: actions,
      ),
    );
  }

  Widget _parcelActions(
    Map<String, dynamic> parcel,
  ) {
    final status =
        parcel['status']?.toString() ?? '';

    if (status == 'RECEIVED') {
      return Padding(
        padding: const EdgeInsets.only(top: 12),
        child: FilledButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _setParcelStatus(
                    parcel,
                    'NOTIFIED',
                  ),
          icon:
              const Icon(Icons.notifications_active),
          label: const Text('Mark Resident Notified'),
        ),
      );
    }

    if (status == 'NOTIFIED') {
      return Padding(
        padding: const EdgeInsets.only(top: 12),
        child: FilledButton.icon(
          onPressed: _isSubmitting
              ? null
              : () => _setParcelStatus(
                    parcel,
                    'COLLECTED',
                  ),
          icon: const Icon(Icons.done_all),
          label: const Text('Mark Collected'),
        ),
      );
    }

    return const SizedBox.shrink();
  }

  Widget _attendanceActions(
    Map<String, dynamic> attendance,
  ) {
    final checkOut = attendance['check_out'];

    if (checkOut != null &&
        checkOut.toString().trim().isNotEmpty) {
      return const SizedBox.shrink();
    }

    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: FilledButton.icon(
        onPressed: _isSubmitting
            ? null
            : () =>
                _checkOutAttendance(attendance),
        icon: const Icon(Icons.logout),
        label: const Text('Check Out Worker'),
      ),
    );
  }

  Widget _detailsFor(
    Map<String, dynamic> item,
  ) {
    final details = <MapEntry<String, dynamic>>[];

    switch (widget.module) {
      case SecurityModuleType.visitors:
        for (final key in [
          'name',
          'phone_number',
          'purpose',
          'flat_name',
          'vehicle_number',
          'status',
          'check_in_time',
          'check_out_time',
          'created_on',
        ]) {
          if (item.containsKey(key)) {
            details.add(MapEntry(key, item[key]));
          }
        }
        break;
      case SecurityModuleType.parcels:
        for (final key in [
          'recipient_name',
          'flat_name',
          'courier_name',
          'tracking_number',
          'status',
          'received_at',
          'collected_at',
          'received_by_name',
        ]) {
          if (item.containsKey(key)) {
            details.add(MapEntry(key, item[key]));
          }
        }
        break;
      case SecurityModuleType.workers:
        for (final key in [
          'name',
          'service_type',
          'phone',
          'id_number',
          'police_verified',
          'is_active',
        ]) {
          if (item.containsKey(key)) {
            details.add(MapEntry(key, item[key]));
          }
        }
        break;
      case SecurityModuleType.attendance:
        for (final key in [
          'worker_name',
          'check_in',
          'check_out',
          'gate_note',
          'recorded_by_name',
        ]) {
          if (item.containsKey(key)) {
            details.add(MapEntry(key, item[key]));
          }
        }
        break;
      case SecurityModuleType.vehicles:
        for (final key in [
          'vehicle_number',
          'owner_name',
          'vehicle_type',
          'flat_name',
          'parking_slot',
          'is_active',
        ]) {
          if (item.containsKey(key)) {
            details.add(MapEntry(key, item[key]));
          }
        }
        break;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        ...details.map(
          (entry) => Padding(
            padding:
                const EdgeInsets.only(bottom: 6),
            child: Row(
              crossAxisAlignment:
                  CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 145,
                  child: Text(
                    '${entry.key.replaceAll('_', ' ')}:',
                    style: const TextStyle(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                Expanded(
                  child: Text(
                    _value(entry.value),
                  ),
                ),
              ],
            ),
          ),
        ),
        if (widget.module ==
            SecurityModuleType.visitors)
          _visitorActions(item),
        if (widget.module ==
            SecurityModuleType.parcels)
          _parcelActions(item),
        if (widget.module ==
            SecurityModuleType.attendance)
          _attendanceActions(item),
      ],
    );
  }

  String _titleFor(
    Map<String, dynamic> item,
    int index,
  ) {
    switch (widget.module) {
      case SecurityModuleType.visitors:
        return item['name']?.toString() ??
            'Visitor ${index + 1}';
      case SecurityModuleType.parcels:
        return item['recipient_name']?.toString() ??
            'Parcel ${index + 1}';
      case SecurityModuleType.workers:
        return item['name']?.toString() ??
            'Worker ${index + 1}';
      case SecurityModuleType.attendance:
        return item['worker_name']?.toString() ??
            'Attendance ${index + 1}';
      case SecurityModuleType.vehicles:
        return item['vehicle_number']?.toString() ??
            'Vehicle ${index + 1}';
    }
  }

  String? _subtitleFor(
    Map<String, dynamic> item,
  ) {
    switch (widget.module) {
      case SecurityModuleType.visitors:
        return '${item['flat_name'] ?? ''} • ${item['status'] ?? ''}';
      case SecurityModuleType.parcels:
        return '${item['courier_name'] ?? ''} • ${item['status'] ?? ''}';
      case SecurityModuleType.workers:
        return '${item['service_type'] ?? ''} • ${item['is_active'] == false ? 'Inactive' : 'Active'}';
      case SecurityModuleType.attendance:
        return item['check_out'] == null
            ? 'Currently inside'
            : 'Checked out';
      case SecurityModuleType.vehicles:
        return '${item['owner_name'] ?? ''} • ${item['flat_name'] ?? ''}';
    }
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filteredItems;

    return Scaffold(
      appBar: AppBar(
        title: Text(_title),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadItems,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton:
          _showCheckInButton
              ? FloatingActionButton.extended(
                  onPressed: _isSubmitting
                      ? null
                      : _showWorkerCheckInDialog,
                  icon: const Icon(Icons.login),
                  label:
                      const Text('Worker Check In'),
                )
              : null,
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _error != null
              ? Center(
                  child: Padding(
                    padding:
                        const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment:
                          MainAxisAlignment.center,
                      children: [
                        const Icon(
                          Icons.error_outline,
                          size: 50,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _error!,
                          textAlign:
                              TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: _loadItems,
                          child:
                              const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : Column(
                  children: [
                    if (_showSearch)
                      Padding(
                        padding:
                            const EdgeInsets.all(16),
                        child: TextField(
                          decoration:
                              InputDecoration(
                            prefixIcon:
                                const Icon(
                              Icons.search,
                            ),
                            hintText:
                                'Search $_title',
                            border:
                                const OutlineInputBorder(),
                          ),
                          onChanged: (value) {
                            setState(() {
                              _search = value;
                            });
                          },
                        ),
                      ),
                    Expanded(
                      child: RefreshIndicator(
                        onRefresh: _loadItems,
                        child: filtered.isEmpty
                            ? ListView(
                                physics:
                                    const AlwaysScrollableScrollPhysics(),
                                children: [
                                  SizedBox(
                                    height: 420,
                                    child: Center(
                                      child: Text(
                                        'No records found.',
                                      ),
                                    ),
                                  ),
                                ],
                              )
                            : ListView.builder(
                                padding:
                                    const EdgeInsets.fromLTRB(
                                  16,
                                  0,
                                  16,
                                  100,
                                ),
                                itemCount:
                                    filtered.length,
                                itemBuilder:
                                    (context, index) {
                                  final raw =
                                      filtered[index];

                                  if (raw is! Map) {
                                    return const SizedBox
                                        .shrink();
                                  }

                                  final item =
                                      Map<String, dynamic>
                                          .from(raw);

                                  return Card(
                                    margin:
                                        const EdgeInsets.only(
                                      bottom: 12,
                                    ),
                                    child:
                                        ExpansionTile(
                                      leading:
                                          CircleAvatar(
                                        child:
                                            Icon(_icon),
                                      ),
                                      title: Text(
                                        _titleFor(
                                          item,
                                          index,
                                        ),
                                        style:
                                            const TextStyle(
                                          fontWeight:
                                              FontWeight
                                                  .bold,
                                        ),
                                      ),
                                      subtitle: Text(
                                        _subtitleFor(
                                              item,
                                            ) ??
                                            '',
                                      ),
                                      children: [
                                        Padding(
                                          padding:
                                              const EdgeInsets
                                                  .fromLTRB(
                                            16,
                                            0,
                                            16,
                                            16,
                                          ),
                                          child:
                                              _detailsFor(
                                            item,
                                          ),
                                        ),
                                      ],
                                    ),
                                  );
                                },
                              ),
                      ),
                    ),
                  ],
                ),
    );
  }
}

class ResidentDashboardScreen extends StatefulWidget {
  final String username;

  const ResidentDashboardScreen({
    super.key,
    required this.username,
  });

  @override
  State<ResidentDashboardScreen> createState() =>
      _ResidentDashboardScreenState();
}

class _ResidentDashboardScreenState
    extends State<ResidentDashboardScreen> {
  final _storage = const FlutterSecureStorage();

  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  String? _error;

  Map<String, dynamic>? _resident;
  Map<String, dynamic>? _dashboard;

  List<dynamic> _recentNotices = [];
  List<dynamic> _upcomingEvents = [];

  @override
  void initState() {
    super.initState();
    _loadDashboard();
  }

  Future<void> _loadDashboard() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(
        key: 'access_token',
      );

      if (token == null) {
        setState(() {
          _error = 'Login token not found.';
          _isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse(
          '$baseUrl/dashboard/resident/',
        ),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 &&
          data['success'] == true) {
        setState(() {
          _resident =
              Map<String, dynamic>.from(data['resident']);

          _dashboard =
              Map<String, dynamic>.from(data['dashboard']);

          _recentNotices =
              data['recent_notices'] ?? [];

          _upcomingEvents =
              data['upcoming_events'] ?? [];

          _isLoading = false;
        });
      } else {
        setState(() {
          _error =
              data['message'] ?? 'Unable to load dashboard.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Unable to connect to the server.';
        _isLoading = false;
      });
    }
  }

  Future<void> _logout() async {
    await _storage.deleteAll();

    if (!mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => const LoginScreen(),
      ),
      (route) => false,
    );
  }

  // Responsive Resident dashboard card.
  Widget _actionDashboardCard({
    required String title,
    required String value,
    required IconData icon,
    required Widget page,
  }) {
    return Card(
      margin: EdgeInsets.zero,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
      ),
      child: InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () async {
          await Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => page),
          );
          if (mounted) {
            _loadDashboard();
          }
        },
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: 10,
            vertical: 12,
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 30),
              const SizedBox(height: 7),
              FittedBox(
                fit: BoxFit.scaleDown,
                child: Text(
                  value,
                  maxLines: 1,
                  textAlign: TextAlign.center,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(height: 5),
              Text(
                title,
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  fontSize: 13,
                  height: 1.15,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _serviceButton({
    required String title,
    required IconData icon,
    required Widget page,
  }) {
    return SizedBox(
      width: 190,
      child: Card(
        child: ListTile(
          leading: Icon(icon),
          title: Text(title),
          trailing: const Icon(Icons.chevron_right),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => page),
            );
          },
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Resident Dashboard',
        ),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadDashboard,
            icon: const Icon(
              Icons.refresh,
            ),
          ),
          IconButton(
            tooltip: 'Logout',
            onPressed: _logout,
            icon: const Icon(
              Icons.logout,
            ),
          ),
        ],
      ),

      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment:
                        MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 50,
                      ),
                      const SizedBox(height: 12),
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _loadDashboard,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadDashboard,
                  child: ListView(
                    padding: const EdgeInsets.all(20),
                    children: [
                      Card(
                        child: Padding(
                          padding:
                              const EdgeInsets.all(20),
                          child: Row(
                            children: [
                              const CircleAvatar(
                                radius: 32,
                                child: Icon(
                                  Icons.person,
                                  size: 34,
                                ),
                              ),
                              const SizedBox(width: 16),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment:
                                      CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _resident?['name'] ??
                                          widget.username,
                                      style:
                                          Theme.of(context)
                                              .textTheme
                                              .titleLarge
                                              ?.copyWith(
                                                fontWeight:
                                                    FontWeight.bold,
                                              ),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Flat: ${_resident?['flat'] ?? '-'}',
                                    ),
                                    Text(
                                      'Username: ${_resident?['username'] ?? widget.username}',
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),

                      const SizedBox(height: 20),

                      Text(
                        'Overview',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),

                      const SizedBox(height: 12),

                      GridView.count(
                        crossAxisCount:
                            MediaQuery.of(context)
                                        .size
                                        .width >
                                    700
                                ? 4
                                : 2,
                        shrinkWrap: true,
                        physics:
                            const NeverScrollableScrollPhysics(),
                        crossAxisSpacing: 12,
                        mainAxisSpacing: 12,
                        childAspectRatio: 1.0,
                        children: [
                          _actionDashboardCard(
                            title: 'Pending Invoices',
                            value:
                                '${_dashboard?['pending_invoices'] ?? 0}',
                            icon: Icons.receipt_long,
                            page: const BillsScreen(),
                          ),
                          _actionDashboardCard(
                            title: 'Outstanding',
                            value:
                                '₹${_dashboard?['outstanding_amount'] ?? 0}',
                            icon: Icons.account_balance_wallet,
                            page: const BillsScreen(),
                          ),
                          _actionDashboardCard(
                            title: 'Open Complaints',
                            value:
                                '${_dashboard?['open_complaints'] ?? 0}',
                            icon: Icons.report_problem,
                            page: const ComplaintsScreen(),
                          ),
                          _actionDashboardCard(
                            title: 'Parcels Waiting',
                            value:
                                '${_dashboard?['parcels_waiting'] ?? 0}',
                            icon: Icons.inventory_2,
                            page: const ResidentDataScreen(
                              title: 'My Parcels',
                              endpoint: 'parcels/',
                              responseKey: 'parcels',
                              icon: Icons.inventory_2,
                            ),
                          ),
                          _actionDashboardCard(
                            title: 'Amenity Bookings',
                            value:
                                '${_dashboard?['upcoming_amenity_bookings'] ?? 0}',
                            icon: Icons.pool,
                            page: const ResidentDataScreen(
                              title: 'My Amenity Bookings',
                              endpoint: 'amenities/bookings/',
                              responseKey: 'bookings',
                              icon: Icons.pool,
                              actionType: 'amenity_booking',
                            ),
                          ),
                          _actionDashboardCard(
                            title: 'Active Vehicles',
                            value:
                                '${_dashboard?['active_vehicles'] ?? 0}',
                            icon: Icons.directions_car,
                            page: const ResidentDataScreen(
                              title: 'My Vehicles',
                              endpoint: 'vehicles/',
                              responseKey: 'vehicles',
                              icon: Icons.directions_car,
                              actionType: 'vehicle',
                            ),
                          ),
                          _actionDashboardCard(
                            title: 'Certificates',
                            value:
                                '${_dashboard?['pending_certificates'] ?? 0}',
                            icon: Icons.description,
                            page: const ResidentDataScreen(
                              title: 'Certificate Requests',
                              endpoint: 'certificate-requests/',
                              responseKey: 'certificate_requests',
                              icon: Icons.description,
                              actionType: 'certificate',
                            ),
                          ),
                          _actionDashboardCard(
                            title: 'Move Requests',
                            value:
                                '${_dashboard?['pending_move_requests'] ?? 0}',
                            icon: Icons.local_shipping,
                            page: const ResidentDataScreen(
                              title: 'My Move Requests',
                              endpoint: 'move-requests/',
                              responseKey: 'move_requests',
                              icon: Icons.local_shipping,
                              actionType: 'move_request',
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 28),

                      Text(
                        'Resident Services',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),

                      const SizedBox(height: 10),

                      Wrap(
                        spacing: 10,
                        runSpacing: 10,
                        children: [
                          _serviceButton(
                            title: 'All Notices',
                            icon: Icons.campaign,
                            page: const ResidentDataScreen(
                              title: 'Notices',
                              endpoint: 'notices/',
                              responseKey: 'notices',
                              icon: Icons.campaign,
                            ),
                          ),
                          _serviceButton(
                            title: 'Events',
                            icon: Icons.event,
                            page: const ResidentDataScreen(
                              title: 'Society Events',
                              endpoint: 'events/',
                              responseKey: 'events',
                              icon: Icons.event,
                            ),
                          ),
                          _serviceButton(
                            title: 'Visitors',
                            icon: Icons.people,
                            page: const ResidentDataScreen(
                              title: 'Visitors',
                              endpoint: 'visitors/',
                              responseKey: 'visitors',
                              icon: Icons.people,
                              actionType: 'visitor',
                            ),
                          ),
                          _serviceButton(
                            title: 'Polls',
                            icon: Icons.poll,
                            page: const ResidentDataScreen(
                              title: 'Polls',
                              endpoint: 'polls/',
                              responseKey: 'polls',
                              icon: Icons.poll,
                              actionType: 'poll_vote',
                            ),
                          ),
                          _serviceButton(
                            title: 'Amenities',
                            icon: Icons.sports_tennis,
                            page: const ResidentDataScreen(
                              title: 'Available Amenities',
                              endpoint: 'amenities/',
                              responseKey: 'amenities',
                              icon: Icons.sports_tennis,
                            ),
                          ),
                          _serviceButton(
                            title: 'Domestic Workers',
                            icon: Icons.badge,
                            page: const ResidentDataScreen(
                              title: 'Domestic Workers',
                              endpoint: 'domestic-workers/',
                              responseKey: 'domestic_workers',
                              icon: Icons.badge,
                            ),
                          ),
                          _serviceButton(
                            title: 'Meetings',
                            icon: Icons.groups,
                            page: const ResidentDataScreen(
                              title: 'Society Meetings',
                              endpoint: 'meetings/',
                              responseKey: 'meetings',
                              icon: Icons.groups,
                            ),
                          ),
                          _serviceButton(
                            title: 'Emergency Contacts',
                            icon: Icons.emergency,
                            page: const ResidentDataScreen(
                              title: 'Emergency Contacts',
                              endpoint: 'emergency-contacts/',
                              responseKey: 'emergency_contacts',
                              icon: Icons.emergency,
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 28),

                      Text(
                        'Recent Notices',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),

                      const SizedBox(height: 10),

                      if (_recentNotices.isEmpty)
                        const Card(
                          child: Padding(
                            padding: EdgeInsets.all(18),
                            child: Text(
                              'No recent notices.',
                            ),
                          ),
                        )
                      else
                        ..._recentNotices.map(
                          (notice) => Card(
                            child: ListTile(
                              leading: Icon(
                                notice['pinned'] == true
                                    ? Icons.push_pin
                                    : Icons.campaign,
                              ),
                              title: Text(
                                notice['title'] ?? '',
                              ),
                              subtitle: Text(
                                notice['category'] ??
                                    'GENERAL',
                              ),
                            ),
                          ),
                        ),

                      const SizedBox(height: 28),

                      Text(
                        'Upcoming Events',
                        style: Theme.of(context)
                            .textTheme
                            .titleLarge
                            ?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),

                      const SizedBox(height: 10),

                      if (_upcomingEvents.isEmpty)
                        const Card(
                          child: Padding(
                            padding: EdgeInsets.all(18),
                            child: Text(
                              'No upcoming events.',
                            ),
                          ),
                        )
                      else
                        ..._upcomingEvents.map(
                          (event) => Card(
                            child: ListTile(
                              leading:
                                  const Icon(Icons.event),
                              title: Text(
                                event['title'] ?? '',
                              ),
                              subtitle: Text(
                                event['venue'] ?? '',
                              ),
                            ),
                          ),
                        ),

                      const SizedBox(height: 30),
                    ],
                  ),
                ),
    );
  }
}
// ============================================================
// COMMON DASHBOARD
// ============================================================

class DashboardLayout extends StatelessWidget {
  final String title;
  final String username;
  final String role;
  final IconData icon;
  final List<DashboardMenuItem> menuItems;

  const DashboardLayout({
    super.key,
    required this.title,
    required this.username,
    required this.role,
    required this.icon,
    required this.menuItems,
  });

  Future<void> _logout(BuildContext context) async {
    const storage = FlutterSecureStorage();

    await storage.deleteAll();

    if (!context.mounted) return;

    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(
        builder: (_) => const LoginScreen(),
      ),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        actions: [
          IconButton(
            tooltip: 'Logout',
            onPressed: () => _logout(context),
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  child: Icon(
                    icon,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                Column(
                  crossAxisAlignment:
                      CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome, $username',
                      style: Theme.of(context)
                          .textTheme
                          .titleLarge
                          ?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    Text(
                      'Role: $role',
                    ),
                  ],
                ),
              ],
            ),

            const SizedBox(height: 30),

            Expanded(
              child: GridView.builder(
                gridDelegate:
                    const SliverGridDelegateWithMaxCrossAxisExtent(
                  maxCrossAxisExtent: 220,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                  childAspectRatio: 1.4,
                ),
                itemCount: menuItems.length,
                itemBuilder: (context, index) {
                  final item = menuItems[index];

                  return Card(
                    child: InkWell(
                      borderRadius:
                          BorderRadius.circular(12),
                      onTap: () {
                        ScaffoldMessenger.of(context)
                            .showSnackBar(
                          SnackBar(
                            content: Text(
                              '${item.title} screen coming next',
                            ),
                          ),
                        );
                      },
                      child: Padding(
                        padding:
                            const EdgeInsets.all(16),
                        child: Column(
                          mainAxisAlignment:
                              MainAxisAlignment.center,
                          children: [
                            Icon(
                              item.icon,
                              size: 36,
                            ),
                            const SizedBox(height: 10),
                            Text(
                              item.title,
                              textAlign:
                                  TextAlign.center,
                              style: const TextStyle(
                                fontWeight:
                                    FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}


class DashboardMenuItem {
  final String title;
  final IconData icon;

  const DashboardMenuItem({
    required this.title,
    required this.icon,
  });
}




// ============================================================
// GENERIC RESIDENT API LIST SCREEN
// ============================================================

class ResidentDataScreen extends StatefulWidget {
  final String title;
  final String endpoint;
  final String responseKey;
  final IconData icon;
  final String? actionType;

  const ResidentDataScreen({
    super.key,
    required this.title,
    required this.endpoint,
    required this.responseKey,
    required this.icon,
    this.actionType,
  });

  @override
  State<ResidentDataScreen> createState() => _ResidentDataScreenState();
}

class _ResidentDataScreenState extends State<ResidentDataScreen> {
  final _storage = const FlutterSecureStorage();
  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  bool _isSubmitting = false;
  String? _error;
  List<dynamic> _items = [];

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<String?> _token() {
    return _storage.read(key: 'access_token');
  }

  Map<String, String> _headers(String token) {
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  Future<void> _loadItems() async {
    if (mounted) {
      setState(() {
        _isLoading = true;
        _error = null;
      });
    }

    try {
      final token = await _token();

      if (token == null) {
        if (mounted) {
          setState(() {
            _error = 'Login token not found.';
            _isLoading = false;
          });
        }
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/${widget.endpoint}'),
        headers: _headers(token),
      );

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200) {
        List<dynamic> items = [];

        if (data is Map<String, dynamic>) {
          final preferred = data[widget.responseKey];

          if (preferred is List) {
            items = preferred;
          } else {
            for (final value in data.values) {
              if (value is List) {
                items = value;
                break;
              }
            }
          }
        } else if (data is List) {
          items = data;
        }

        if (mounted) {
          setState(() {
            _items = items;
            _isLoading = false;
          });
        }
      } else {
        final message = _messageFromResponse(
          data,
          'Unable to load ${widget.title}.',
        );

        if (mounted) {
          setState(() {
            _error = '$message (HTTP ${response.statusCode})';
            _isLoading = false;
          });
        }
      }
    } catch (_) {
      if (mounted) {
        setState(() {
          _error = 'Unable to connect to the server.';
          _isLoading = false;
        });
      }
    }
  }

  String _messageFromResponse(dynamic data, String fallback) {
    if (data is Map<String, dynamic>) {
      final message = data['message'];
      if (message != null && message.toString().trim().isNotEmpty) {
        return message.toString();
      }

      final detail = data['detail'];
      if (detail != null && detail.toString().trim().isNotEmpty) {
        return detail.toString();
      }

      final errors = data['errors'];
      if (errors != null) {
        return errors.toString();
      }
    }
    return fallback;
  }

  Future<bool> _postJson(
    String endpoint,
    Map<String, dynamic> body, {
    String successMessage = 'Saved successfully.',
  }) async {
    if (_isSubmitting) return false;

    setState(() => _isSubmitting = true);

    try {
      final token = await _token();
      if (token == null) {
        _showMessage('Login token not found.');
        return false;
      }

      final response = await http.post(
        Uri.parse('$baseUrl/$endpoint'),
        headers: _headers(token),
        body: jsonEncode(body),
      );

      dynamic data;
      try {
        data = jsonDecode(response.body);
      } catch (_) {
        data = null;
      }

      if (response.statusCode == 200 || response.statusCode == 201) {
        _showMessage(
          data is Map<String, dynamic> && data['message'] != null
              ? data['message'].toString()
              : successMessage,
        );
        await _loadItems();
        return true;
      }

      _showMessage(
        _messageFromResponse(
          data,
          'Request failed (HTTP ${response.statusCode}).',
        ),
      );
      return false;
    } catch (_) {
      _showMessage('Unable to connect to the server.');
      return false;
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  String _label(String key) {
    return key
        .replaceAll('_', ' ')
        .split(' ')
        .where((word) => word.isNotEmpty)
        .map(
          (word) =>
              '${word[0].toUpperCase()}${word.substring(1).toLowerCase()}',
        )
        .join(' ');
  }

  String _valueText(dynamic value) {
    if (value == null) return '-';
    if (value is bool) return value ? 'Yes' : 'No';
    if (value is List) {
      if (value.isEmpty) return '-';
      return value.map((item) => item.toString()).join(', ');
    }
    if (value is Map) {
      return value.entries
          .map((entry) => '${entry.key}: ${entry.value}')
          .join(', ');
    }
    final text = value.toString().trim();
    return text.isEmpty ? '-' : text;
  }

  List<MapEntry<String, dynamic>> _visibleEntries(
    Map<String, dynamic> item,
  ) {
    const hiddenKeys = {
      'photo',
      'image',
      'attachment',
      'poster',
      'document',
      'supporting_document',
      'created_by',
      'updated_by',
      'options',
    };

    return item.entries
        .where((entry) => !hiddenKeys.contains(entry.key))
        .take(10)
        .toList();
  }

  String _titleForItem(Map<String, dynamic> item, int index) {
    const possibleKeys = [
      'title',
      'name',
      'recipient_name',
      'vehicle_number',
      'request_type',
      'purpose',
      'question',
      'subject',
      'amenity_name',
    ];

    for (final key in possibleKeys) {
      final value = item[key];
      if (value != null && value.toString().trim().isNotEmpty) {
        return value.toString();
      }
    }

    final id = item['id'];
    if (id != null) {
      return '${widget.title} #$id';
    }

    return '${widget.title} ${index + 1}';
  }

  bool get _hasCreateAction {
    return const {
      'visitor',
      'amenity_booking',
      'vehicle',
      'certificate',
      'move_request',
    }.contains(widget.actionType);
  }

  String get _actionTooltip {
    switch (widget.actionType) {
      case 'visitor':
        return 'Add visitor';
      case 'amenity_booking':
        return 'Book amenity';
      case 'vehicle':
        return 'Add vehicle';
      case 'certificate':
        return 'Request certificate';
      case 'move_request':
        return 'Create move request';
      default:
        return 'Add';
    }
  }

  Future<void> _openCreateAction() async {
    switch (widget.actionType) {
      case 'visitor':
        await _showVisitorDialog();
        break;
      case 'amenity_booking':
        await _showAmenityBookingDialog();
        break;
      case 'vehicle':
        await _showVehicleDialog();
        break;
      case 'certificate':
        await _showCertificateDialog();
        break;
      case 'move_request':
        await _showMoveRequestDialog();
        break;
    }
  }

  Future<void> _showVisitorDialog() async {
    final name = TextEditingController();
    final phone = TextEditingController();
    final purpose = TextEditingController();
    final vehicleNumber = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text('Add Visitor'),
          content: SizedBox(
            width: 430,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextField(
                    controller: name,
                    decoration: const InputDecoration(
                      labelText: 'Visitor name *',
                    ),
                  ),
                  TextField(
                    controller: phone,
                    keyboardType: TextInputType.phone,
                    decoration: const InputDecoration(
                      labelText: 'Phone number *',
                    ),
                  ),
                  TextField(
                    controller: purpose,
                    decoration: const InputDecoration(
                      labelText: 'Purpose *',
                    ),
                  ),
                  TextField(
                    controller: vehicleNumber,
                    decoration: const InputDecoration(
                      labelText: 'Vehicle number (optional)',
                    ),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () async {
                if (name.text.trim().isEmpty ||
                    phone.text.trim().isEmpty ||
                    purpose.text.trim().isEmpty) {
                  _showMessage('Name, phone number and purpose are required.');
                  return;
                }

                final success = await _postJson(
                  'visitors/',
                  {
                    'name': name.text.trim(),
                    'phone_number': phone.text.trim(),
                    'purpose': purpose.text.trim(),
                    'vehicle_number': vehicleNumber.text.trim(),
                  },
                  successMessage: 'Visitor added successfully.',
                );

                if (success && dialogContext.mounted) {
                  Navigator.pop(dialogContext);
                }
              },
              child: const Text('Submit'),
            ),
          ],
        );
      },
    );
  }

  Future<List<Map<String, dynamic>>> _fetchAmenities() async {
    final token = await _token();
    if (token == null) return [];

    final response = await http.get(
      Uri.parse('$baseUrl/amenities/'),
      headers: _headers(token),
    );

    if (response.statusCode != 200) return [];

    final data = jsonDecode(response.body);
    if (data is! Map<String, dynamic> || data['amenities'] is! List) {
      return [];
    }

    return (data['amenities'] as List)
        .whereType<Map>()
        .map((item) => Map<String, dynamic>.from(item))
        .toList();
  }

  Future<void> _showAmenityBookingDialog() async {
    List<Map<String, dynamic>> amenities = [];

    try {
      amenities = await _fetchAmenities();
    } catch (_) {
      _showMessage('Unable to load available amenities.');
      return;
    }

    if (amenities.isEmpty) {
      _showMessage('No active amenities are available.');
      return;
    }

    int? selectedAmenityId = amenities.first['id'] as int?;
    final bookingDate = TextEditingController();
    final startTime = TextEditingController();
    final endTime = TextEditingController();
    final notes = TextEditingController();

    if (!mounted) return;

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Book Amenity'),
              content: SizedBox(
                width: 430,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      DropdownButtonFormField<int>(
                        initialValue: selectedAmenityId,
                        decoration: const InputDecoration(
                          labelText: 'Amenity *',
                        ),
                        items: amenities
                            .map(
                              (amenity) => DropdownMenuItem<int>(
                                value: amenity['id'] as int?,
                                child: Text(
                                  '${amenity['name'] ?? 'Amenity'}'
                                  ' (₹${amenity['booking_fee'] ?? 0})',
                                ),
                              ),
                            )
                            .toList(),
                        onChanged: (value) {
                          setDialogState(() {
                            selectedAmenityId = value;
                          });
                        },
                      ),
                      TextField(
                        controller: bookingDate,
                        decoration: const InputDecoration(
                          labelText: 'Booking date *',
                          hintText: 'YYYY-MM-DD',
                        ),
                      ),
                      TextField(
                        controller: startTime,
                        decoration: const InputDecoration(
                          labelText: 'Start time *',
                          hintText: 'HH:MM',
                        ),
                      ),
                      TextField(
                        controller: endTime,
                        decoration: const InputDecoration(
                          labelText: 'End time *',
                          hintText: 'HH:MM',
                        ),
                      ),
                      TextField(
                        controller: notes,
                        maxLines: 2,
                        decoration: const InputDecoration(
                          labelText: 'Notes (optional)',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    if (selectedAmenityId == null ||
                        bookingDate.text.trim().isEmpty ||
                        startTime.text.trim().isEmpty ||
                        endTime.text.trim().isEmpty) {
                      _showMessage(
                        'Amenity, booking date, start time and end time are required.',
                      );
                      return;
                    }

                    final success = await _postJson(
                      'amenities/bookings/',
                      {
                        'amenity': selectedAmenityId,
                        'booking_date': bookingDate.text.trim(),
                        'start_time': startTime.text.trim(),
                        'end_time': endTime.text.trim(),
                        'notes': notes.text.trim(),
                      },
                      successMessage: 'Amenity booking requested successfully.',
                    );

                    if (success && dialogContext.mounted) {
                      Navigator.pop(dialogContext);
                    }
                  },
                  child: const Text('Request Booking'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showVehicleDialog() async {
    final ownerName = TextEditingController();
    final vehicleNumber = TextEditingController();
    final parkingSlot = TextEditingController();
    String vehicleType = 'CAR';

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Add Vehicle'),
              content: SizedBox(
                width: 430,
                child: SingleChildScrollView(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextField(
                        controller: ownerName,
                        decoration: const InputDecoration(
                          labelText: 'Owner name *',
                        ),
                      ),
                      TextField(
                        controller: vehicleNumber,
                        decoration: const InputDecoration(
                          labelText: 'Vehicle number *',
                          hintText: 'MH12AB1234',
                        ),
                      ),
                      DropdownButtonFormField<String>(
                        initialValue: vehicleType,
                        decoration: const InputDecoration(
                          labelText: 'Vehicle type *',
                        ),
                        items: const [
                          DropdownMenuItem(
                            value: 'CAR',
                            child: Text('Car'),
                          ),
                          DropdownMenuItem(
                            value: 'BIKE',
                            child: Text('Bike'),
                          ),
                          DropdownMenuItem(
                            value: 'OTHER',
                            child: Text('Other'),
                          ),
                        ],
                        onChanged: (value) {
                          if (value != null) {
                            setDialogState(() {
                              vehicleType = value;
                            });
                          }
                        },
                      ),
                      TextField(
                        controller: parkingSlot,
                        decoration: const InputDecoration(
                          labelText: 'Parking slot (optional)',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    if (ownerName.text.trim().isEmpty ||
                        vehicleNumber.text.trim().isEmpty) {
                      _showMessage('Owner name and vehicle number are required.');
                      return;
                    }

                    final success = await _postJson(
                      'vehicles/',
                      {
                        'owner_name': ownerName.text.trim(),
                        'vehicle_number':
                            vehicleNumber.text.trim().toUpperCase(),
                        'vehicle_type': vehicleType,
                        'parking_slot': parkingSlot.text.trim(),
                        'is_active': true,
                      },
                      successMessage: 'Vehicle registered successfully.',
                    );

                    if (success && dialogContext.mounted) {
                      Navigator.pop(dialogContext);
                    }
                  },
                  child: const Text('Add Vehicle'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showCertificateDialog() async {
    String requestType = 'NOC';
    final purpose = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Request Certificate'),
              content: SizedBox(
                width: 430,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<String>(
                      initialValue: requestType,
                      decoration: const InputDecoration(
                        labelText: 'Certificate type *',
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: 'NOC',
                          child: Text('NOC'),
                        ),
                        DropdownMenuItem(
                          value: 'ADDRESS',
                          child: Text('Address Proof'),
                        ),
                        DropdownMenuItem(
                          value: 'TENANT',
                          child: Text('Tenant Verification Letter'),
                        ),
                        DropdownMenuItem(
                          value: 'PARKING',
                          child: Text('Parking Certificate'),
                        ),
                        DropdownMenuItem(
                          value: 'OTHER',
                          child: Text('Other'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setDialogState(() {
                            requestType = value;
                          });
                        }
                      },
                    ),
                    TextField(
                      controller: purpose,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Purpose',
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    final success = await _postJson(
                      'certificate-requests/',
                      {
                        'request_type': requestType,
                        'purpose': purpose.text.trim(),
                      },
                      successMessage:
                          'Certificate request submitted successfully.',
                    );

                    if (success && dialogContext.mounted) {
                      Navigator.pop(dialogContext);
                    }
                  },
                  child: const Text('Submit Request'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Future<void> _showMoveRequestDialog() async {
    String moveType = 'MOVE_IN';
    final requestedDate = TextEditingController();
    final notes = TextEditingController();

    await showDialog<void>(
      context: context,
      builder: (dialogContext) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('Create Move Request'),
              content: SizedBox(
                width: 430,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    DropdownButtonFormField<String>(
                      initialValue: moveType,
                      decoration: const InputDecoration(
                        labelText: 'Move type *',
                      ),
                      items: const [
                        DropdownMenuItem(
                          value: 'MOVE_IN',
                          child: Text('Move In'),
                        ),
                        DropdownMenuItem(
                          value: 'MOVE_OUT',
                          child: Text('Move Out'),
                        ),
                      ],
                      onChanged: (value) {
                        if (value != null) {
                          setDialogState(() {
                            moveType = value;
                          });
                        }
                      },
                    ),
                    TextField(
                      controller: requestedDate,
                      decoration: const InputDecoration(
                        labelText: 'Requested date *',
                        hintText: 'YYYY-MM-DD',
                      ),
                    ),
                    TextField(
                      controller: notes,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        labelText: 'Notes (optional)',
                      ),
                    ),
                  ],
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(dialogContext),
                  child: const Text('Cancel'),
                ),
                FilledButton(
                  onPressed: () async {
                    if (requestedDate.text.trim().isEmpty) {
                      _showMessage('Requested date is required.');
                      return;
                    }

                    final success = await _postJson(
                      'move-requests/',
                      {
                        'move_type': moveType,
                        'requested_date': requestedDate.text.trim(),
                        'notes': notes.text.trim(),
                      },
                      successMessage: 'Move request submitted successfully.',
                    );

                    if (success && dialogContext.mounted) {
                      Navigator.pop(dialogContext);
                    }
                  },
                  child: const Text('Submit Request'),
                ),
              ],
            );
          },
        );
      },
    );
  }

  Widget _pollOptions(Map<String, dynamic> item) {
    if (widget.actionType != 'poll_vote') {
      return const SizedBox.shrink();
    }

    final options = item['options'];
    final hasVoted = item['user_has_voted'] == true;
    final isActive = item['is_active'] != false;

    if (options is! List || options.isEmpty) {
      return const Padding(
        padding: EdgeInsets.only(top: 8),
        child: Text('No poll options available.'),
      );
    }

    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (hasVoted)
            const Padding(
              padding: EdgeInsets.only(bottom: 8),
              child: Text(
                'You have already voted in this poll.',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ...options.whereType<Map>().map((rawOption) {
            final option = Map<String, dynamic>.from(rawOption);
            final optionId = option['id'];
            final label = option['label']?.toString() ?? 'Option';
            final votes =
                option['vote_count'] ?? option['votes'] ?? option['count'];

            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: OutlinedButton(
                onPressed: hasVoted || !isActive || optionId == null
                    ? null
                    : () async {
                        final pollId = item['id'];
                        if (pollId == null) return;

                        await _postJson(
                          'polls/$pollId/vote/',
                          {'option': optionId},
                          successMessage: 'Vote submitted successfully.',
                        );
                      },
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  child: Row(
                    children: [
                      Expanded(child: Text(label)),
                      if (votes != null) Text('Votes: $votes'),
                    ],
                  ),
                ),
              ),
            );
          }),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadItems,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton: _hasCreateAction
          ? FloatingActionButton.extended(
              onPressed: _isSubmitting ? null : _openCreateAction,
              icon: _isSubmitting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.add),
              label: Text(_actionTooltip),
            )
          : null,
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.error_outline, size: 50),
                        const SizedBox(height: 12),
                        Text(
                          _error!,
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 16),
                        FilledButton(
                          onPressed: _loadItems,
                          child: const Text('Retry'),
                        ),
                      ],
                    ),
                  ),
                )
              : _items.isEmpty
                  ? RefreshIndicator(
                      onRefresh: _loadItems,
                      child: ListView(
                        physics: const AlwaysScrollableScrollPhysics(),
                        children: [
                          SizedBox(
                            height: MediaQuery.of(context).size.height * 0.65,
                            child: Center(
                              child: Text(
                                'No ${widget.title.toLowerCase()} found.',
                              ),
                            ),
                          ),
                        ],
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadItems,
                      child: ListView.builder(
                        padding: const EdgeInsets.fromLTRB(16, 16, 16, 96),
                        itemCount: _items.length,
                        itemBuilder: (context, index) {
                          final rawItem = _items[index];

                          if (rawItem is! Map) {
                            return Card(
                              margin: const EdgeInsets.only(bottom: 12),
                              child: ListTile(
                                leading: Icon(widget.icon),
                                title: Text(rawItem.toString()),
                              ),
                            );
                          }

                          final item = Map<String, dynamic>.from(rawItem);
                          final entries = _visibleEntries(item);

                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: ExpansionTile(
                              leading: CircleAvatar(
                                child: Icon(widget.icon),
                              ),
                              title: Text(
                                _titleForItem(item, index),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              subtitle: item['status'] != null
                                  ? Text('Status: ${item['status']}')
                                  : null,
                              children: [
                                Padding(
                                  padding: const EdgeInsets.fromLTRB(
                                    16,
                                    0,
                                    16,
                                    16,
                                  ),
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      ...entries.map(
                                        (entry) => Padding(
                                          padding: const EdgeInsets.only(
                                            bottom: 6,
                                          ),
                                          child: Row(
                                            crossAxisAlignment:
                                                CrossAxisAlignment.start,
                                            children: [
                                              SizedBox(
                                                width: 145,
                                                child: Text(
                                                  '${_label(entry.key)}:',
                                                  style: const TextStyle(
                                                    fontWeight:
                                                        FontWeight.w600,
                                                  ),
                                                ),
                                              ),
                                              Expanded(
                                                child: Text(
                                                  _valueText(entry.value),
                                                ),
                                              ),
                                            ],
                                          ),
                                        ),
                                      ),
                                      _pollOptions(item),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          );
                        },
                      ),
                    ),
    );
  }
}


// ============================================================
// RESIDENT BILLS / INVOICES
// ============================================================

class BillsScreen extends StatefulWidget {
  const BillsScreen({super.key});

  @override
  State<BillsScreen> createState() => _BillsScreenState();
}

class _BillsScreenState extends State<BillsScreen> {
  final _storage = const FlutterSecureStorage();
  final String baseUrl = 'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  String? _error;
  List<dynamic> _invoices = [];

  @override
  void initState() {
    super.initState();
    _loadInvoices();
  }

  Future<void> _loadInvoices() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(key: 'access_token');

      if (token == null) {
        setState(() {
          _error = 'Login token not found.';
          _isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/billing/invoices/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success'] == true) {
        setState(() {
          _invoices = data['invoices'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error = data['message'] ?? 'Unable to load invoices.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Unable to connect to the server.';
        _isLoading = false;
      });
    }
  }

  String _display(dynamic value, {String fallback = '-'}) {
    if (value == null) return fallback;
    final text = value.toString().trim();
    return text.isEmpty ? fallback : text;
  }

  String _money(dynamic value) {
    if (value == null) return '0.00';
    final number = double.tryParse(value.toString());
    return number == null ? value.toString() : number.toStringAsFixed(2);
  }

  dynamic _firstValue(Map<String, dynamic> invoice, List<String> keys) {
    for (final key in keys) {
      if (invoice.containsKey(key) && invoice[key] != null) {
        return invoice[key];
      }
    }
    return null;
  }

  Color _statusColor(String status) {
    switch (status.toUpperCase()) {
      case 'PAID':
        return Colors.green;
      case 'PARTIAL':
        return Colors.orange;
      case 'OVERDUE':
        return Colors.red;
      default:
        return Colors.blueGrey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Bills'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadInvoices,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 50),
                      const SizedBox(height: 12),
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed: _loadInvoices,
                        child: const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _invoices.isEmpty
                  ? const Center(
                      child: Text('No invoices found.'),
                    )
                  : RefreshIndicator(
                      onRefresh: _loadInvoices,
                      child: ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _invoices.length,
                        itemBuilder: (context, index) {
                          final invoice = Map<String, dynamic>.from(
                            _invoices[index] as Map,
                          );

                          final status = _display(
                            invoice['status'],
                            fallback: 'PENDING',
                          ).toUpperCase();

                          final amount = _firstValue(
                            invoice,
                            ['amount', 'total_amount'],
                          );
                          final paid = _firstValue(
                            invoice,
                            ['amount_paid', 'paid_amount'],
                          );
                          final balance = _firstValue(
                            invoice,
                            ['balance', 'balance_amount', 'outstanding_amount'],
                          );
                          final issueDate = _firstValue(
                            invoice,
                            ['issue_date', 'created_at'],
                          );
                          final dueDate = _firstValue(
                            invoice,
                            ['due_date'],
                          );
                          final chargeName = _firstValue(
                            invoice,
                            [
                              'charge_name',
                              'charge_template_name',
                              'description',
                              'title',
                            ],
                          );

                          return Card(
                            margin: const EdgeInsets.only(bottom: 12),
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      const CircleAvatar(
                                        child: Icon(Icons.receipt_long),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Text(
                                          chargeName != null
                                              ? _display(chargeName)
                                              : 'Invoice #${_display(invoice['id'])}',
                                          style: const TextStyle(
                                            fontSize: 17,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                      Container(
                                        padding: const EdgeInsets.symmetric(
                                          horizontal: 10,
                                          vertical: 6,
                                        ),
                                        decoration: BoxDecoration(
                                          color: _statusColor(status)
                                              .withValues(alpha: 0.15),
                                          borderRadius:
                                              BorderRadius.circular(20),
                                        ),
                                        child: Text(
                                          status,
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            color: _statusColor(status),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'Amount: ₹${_money(amount)}',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  Text('Paid: ₹${_money(paid)}'),
                                  if (balance != null)
                                    Text('Balance: ₹${_money(balance)}'),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Issue Date: ${_display(issueDate)}',
                                  ),
                                  Text(
                                    'Due Date: ${_display(dueDate)}',
                                  ),
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    ),
    );
  }
}

// ============================================================
// RESIDENT COMPLAINTS
// ============================================================

class ComplaintsScreen extends StatefulWidget {
  const ComplaintsScreen({super.key});

  @override
  State<ComplaintsScreen> createState() =>
      _ComplaintsScreenState();
}

class _ComplaintsScreenState
    extends State<ComplaintsScreen> {
  final _storage = const FlutterSecureStorage();

  final String baseUrl =
      'http://10.0.2.2:8000/api';

  bool _isLoading = true;
  String? _error;

  List<dynamic> _complaints = [];

  @override
  void initState() {
    super.initState();
    _loadComplaints();
  }

  Future<void> _loadComplaints() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final token = await _storage.read(
        key: 'access_token',
      );

      if (token == null) {
        setState(() {
          _error = 'Login token not found.';
          _isLoading = false;
        });
        return;
      }

      final response = await http.get(
        Uri.parse('$baseUrl/complaints/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 &&
          data['success'] == true) {
        setState(() {
          _complaints = data['complaints'] ?? [];
          _isLoading = false;
        });
      } else {
        setState(() {
          _error =
              data['message'] ??
              'Unable to load complaints.';
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error =
            'Unable to connect to the server.';
        _isLoading = false;
      });
    }
  }

  Future<void> _openCreateComplaint() async {
    final created =
        await showDialog<bool>(
      context: context,
      builder: (_) =>
          const CreateComplaintDialog(),
    );

    if (created == true) {
      await _loadComplaints();
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'RESOLVED':
        return Colors.green;
      case 'IN_PROGRESS':
        return Colors.orange;
      case 'CLOSED':
        return Colors.grey;
      default:
        return Colors.red;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Complaints'),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _loadComplaints,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),

      floatingActionButton:
          FloatingActionButton.extended(
        onPressed: _openCreateComplaint,
        icon: const Icon(Icons.add),
        label: const Text('New Complaint'),
      ),

      body: _isLoading
          ? const Center(
              child:
                  CircularProgressIndicator(),
            )
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment:
                        MainAxisAlignment.center,
                    children: [
                      const Icon(
                        Icons.error_outline,
                        size: 50,
                      ),
                      const SizedBox(height: 12),
                      Text(_error!),
                      const SizedBox(height: 16),
                      FilledButton(
                        onPressed:
                            _loadComplaints,
                        child:
                            const Text('Retry'),
                      ),
                    ],
                  ),
                )
              : _complaints.isEmpty
                  ? const Center(
                      child: Text(
                        'No complaints found.',
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh:
                          _loadComplaints,
                      child: ListView.builder(
                        padding:
                            const EdgeInsets.all(
                                16),
                        itemCount:
                            _complaints.length,
                        itemBuilder:
                            (context, index) {
                          final complaint =
                              _complaints[index];

                          final status =
                              complaint[
                                      'status'] ??
                                  'OPEN';

                          return Card(
                            margin:
                                const EdgeInsets
                                    .only(
                              bottom: 12,
                            ),
                            child: ListTile(
                              leading:
                                  const CircleAvatar(
                                child: Icon(
                                  Icons
                                      .report_problem,
                                ),
                              ),
                              title: Text(
                                complaint[
                                        'title'] ??
                                    '',
                                style:
                                    const TextStyle(
                                  fontWeight:
                                      FontWeight
                                          .bold,
                                ),
                              ),
                              subtitle: Column(
                                crossAxisAlignment:
                                    CrossAxisAlignment
                                        .start,
                                children: [
                                  const SizedBox(
                                      height: 6),
                                  Text(
                                    'Category: ${complaint['category'] ?? '-'}',
                                  ),
                                  Text(
                                    'Priority: ${complaint['priority'] ?? '-'}',
                                  ),
                                  Text(
                                    complaint[
                                            'description'] ??
                                        '',
                                    maxLines: 2,
                                    overflow:
                                        TextOverflow
                                            .ellipsis,
                                  ),
                                ],
                              ),
                              trailing:
                                  Container(
                                padding:
                                    const EdgeInsets
                                        .symmetric(
                                  horizontal: 10,
                                  vertical: 6,
                                ),
                                decoration:
                                    BoxDecoration(
                                  color:
                                      _statusColor(
                                    status,
                                  ).withValues(
                                    alpha: 0.15,
                                  ),
                                  borderRadius:
                                      BorderRadius
                                          .circular(
                                              20),
                                ),
                                child: Text(
                                  status,
                                  style:
                                      TextStyle(
                                    fontWeight:
                                        FontWeight
                                            .bold,
                                    color:
                                        _statusColor(
                                      status,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      ),
                    ),
    );
  }
}


// ============================================================
// CREATE COMPLAINT
// ============================================================

class CreateComplaintDialog
    extends StatefulWidget {
  const CreateComplaintDialog({
    super.key,
  });

  @override
  State<CreateComplaintDialog>
      createState() =>
          _CreateComplaintDialogState();
}

class _CreateComplaintDialogState
    extends State<CreateComplaintDialog> {
  final _storage =
      const FlutterSecureStorage();

  final _titleController =
      TextEditingController();

  final _descriptionController =
      TextEditingController();

  final String baseUrl =
      'http://10.0.2.2:8000/api';

  String _category = 'PLUMBING';
  String _priority = 'MEDIUM';

  bool _isSaving = false;

  final List<String> categories = [
    'PLUMBING',
    'ELECTRICAL',
    'SECURITY',
    'CLEANLINESS',
    'NOISE',
    'PARKING',
    'OTHER',
  ];

  final List<String> priorities = [
    'LOW',
    'MEDIUM',
    'HIGH',
  ];

  Future<void> _submit() async {
    if (_titleController.text
            .trim()
            .isEmpty ||
        _descriptionController.text
            .trim()
            .isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Title and description are required.',
          ),
        ),
      );
      return;
    }

    setState(() {
      _isSaving = true;
    });

    try {
      final token =
          await _storage.read(
        key: 'access_token',
      );

      if (token == null) {
        throw Exception(
          'Token not found',
        );
      }

      final response =
          await http.post(
        Uri.parse(
          '$baseUrl/complaints/',
        ),
        headers: {
          'Authorization':
              'Bearer $token',
          'Content-Type':
              'application/json',
        },
        body: jsonEncode({
          'category': _category,
          'title':
              _titleController.text
                  .trim(),
          'description':
              _descriptionController
                  .text
                  .trim(),
          'priority': _priority,
        }),
      );

      final data =
          jsonDecode(response.body);

      if (response.statusCode ==
              201 &&
          data['success'] == true) {
        if (!mounted) return;

        Navigator.pop(
          context,
          true,
        );
      } else {
        if (!mounted) return;

        ScaffoldMessenger.of(context)
            .showSnackBar(
          SnackBar(
            content: Text(
              data['message'] ??
                  data['errors']
                      ?.toString() ??
                  'Unable to create complaint.',
            ),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;

      ScaffoldMessenger.of(context)
          .showSnackBar(
        const SnackBar(
          content: Text(
            'Unable to connect to the server.',
          ),
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isSaving = false;
        });
      }
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title:
          const Text('New Complaint'),
      content: SizedBox(
        width: 420,
        child:
            SingleChildScrollView(
          child: Column(
            mainAxisSize:
                MainAxisSize.min,
            children: [
              DropdownButtonFormField<
                  String>(
                initialValue:
                    _category,
                decoration:
                    const InputDecoration(
                  labelText:
                      'Category',
                  border:
                      OutlineInputBorder(),
                ),
                items: categories
                    .map(
                      (category) =>
                          DropdownMenuItem(
                        value:
                            category,
                        child:
                            Text(
                          category,
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  if (value !=
                      null) {
                    setState(() {
                      _category =
                          value;
                    });
                  }
                },
              ),

              const SizedBox(
                  height: 14),

              TextField(
                controller:
                    _titleController,
                decoration:
                    const InputDecoration(
                  labelText: 'Title',
                  border:
                      OutlineInputBorder(),
                ),
              ),

              const SizedBox(
                  height: 14),

              TextField(
                controller:
                    _descriptionController,
                maxLines: 4,
                decoration:
                    const InputDecoration(
                  labelText:
                      'Description',
                  border:
                      OutlineInputBorder(),
                ),
              ),

              const SizedBox(
                  height: 14),

              DropdownButtonFormField<
                  String>(
                initialValue:
                    _priority,
                decoration:
                    const InputDecoration(
                  labelText:
                      'Priority',
                  border:
                      OutlineInputBorder(),
                ),
                items: priorities
                    .map(
                      (priority) =>
                          DropdownMenuItem(
                        value:
                            priority,
                        child:
                            Text(
                          priority,
                        ),
                      ),
                    )
                    .toList(),
                onChanged: (value) {
                  if (value !=
                      null) {
                    setState(() {
                      _priority =
                          value;
                    });
                  }
                },
              ),
            ],
          ),
        ),
      ),
      actions: [
        TextButton(
          onPressed:
              _isSaving
                  ? null
                  : () =>
                      Navigator.pop(
                        context,
                        false,
                      ),
          child:
              const Text('Cancel'),
        ),
        FilledButton(
          onPressed:
              _isSaving
                  ? null
                  : _submit,
          child: _isSaving
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child:
                      CircularProgressIndicator(
                    strokeWidth: 2,
                  ),
                )
              : const Text(
                  'Submit',
                ),
        ),
      ],
    );
  }
}