import 'package:flutter/material.dart';

void main() {
  runApp(const TeenPattiPro());
}

class TeenPattiPro extends StatelessWidget {
  const TeenPattiPro({super.key});

  @override
  Widget build(BuildContext context) {

    return MaterialApp(

      debugShowCheckedModeBanner: false,

      title: 'Teen Patti Pro',

      theme: ThemeData(

        brightness: Brightness.dark,

        scaffoldBackgroundColor: const Color(0xFF0B0B0B),

        fontFamily: 'Poppins',

        primaryColor: Colors.amber,

        colorScheme: ColorScheme.dark(

          primary: Colors.amber.shade600,
        ),
      ),

      home: const HomeScreen(),
    );
  }
}

# ================= HOME SCREEN =================

class HomeScreen extends StatefulWidget {

  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() =>
      _HomeScreenState();
}

class _HomeScreenState
    extends State<HomeScreen> {

  final List<TableModel> tables = [

    TableModel(
      tableName: "Beginner Table",
      bootAmount: 1,
      players: 3,
      maxPlayers: 5,
    ),

    TableModel(
      tableName: "Silver Table",
      bootAmount: 5,
      players: 5,
      maxPlayers: 5,
    ),

    TableModel(
      tableName: "Gold Table",
      bootAmount: 10,
      players: 2,
      maxPlayers: 5,
    ),

    TableModel(
      tableName: "VIP Table",
      bootAmount: 50,
      players: 4,
      maxPlayers: 5,
    ),
  ];

  @override
  Widget build(BuildContext context) {

    return Scaffold(

      appBar: AppBar(

        elevation: 0,

        backgroundColor: Colors.black,

        title: const Text(

          "Teen Patti Pro",

          style: TextStyle(
            color: Colors.amber,
            fontWeight: FontWeight.bold,
          ),
        ),

        actions: [

          Padding(

            padding: const EdgeInsets.all(12),

            child: Container(

              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 6,
              ),

              decoration: BoxDecoration(

                color: Colors.amber.shade700,

                borderRadius: BorderRadius.circular(20),
              ),

              child: const Row(

                children: [

                  Icon(
                    Icons.account_balance_wallet,
                    color: Colors.black,
                    size: 18,
                  ),

                  SizedBox(width: 5),

                  Text(

                    "₹ 25,000",

                    style: TextStyle(
                      color: Colors.black,
                      fontWeight: FontWeight.bold,
                    ),
                  )
                ],
              ),
            ),
          )
        ],
      ),

      body: Column(

        children: [

          # ================= PROFILE =================

          Container(

            margin: const EdgeInsets.all(16),

            padding: const EdgeInsets.all(16),

            decoration: BoxDecoration(

              gradient: LinearGradient(

                colors: [
                  Colors.amber.shade700,
                  Colors.orange.shade900,
                ],
              ),

              borderRadius: BorderRadius.circular(25),
            ),

            child: Row(

              children: [

                CircleAvatar(

                  radius: 35,

                  backgroundColor: Colors.black,

                  child: Icon(
                    Icons.person,
                    size: 40,
                    color: Colors.amber,
                  ),
                ),

                const SizedBox(width: 15),

                const Expanded(

                  child: Column(

                    crossAxisAlignment:
                        CrossAxisAlignment.start,

                    children: [

                      Text(

                        "Sujit Falia",

                        style: TextStyle(

                          fontSize: 22,

                          fontWeight:
                              FontWeight.bold,

                          color: Colors.black,
                        ),
                      ),

                      SizedBox(height: 5),

                      Text(

                        "VIP PLAYER",

                        style: TextStyle(

                          color: Colors.black87,

                          fontWeight:
                              FontWeight.w600,
                        ),
                      ),
                    ],
                  ),
                ),

                ElevatedButton(

                  style: ElevatedButton.styleFrom(

                    backgroundColor: Colors.black,

                    shape: RoundedRectangleBorder(

                      borderRadius:
                          BorderRadius.circular(15),
                    ),
                  ),

                  onPressed: () {},

                  child: const Text(

                    "ADD CASH",

                    style: TextStyle(
                      color: Colors.amber,
                    ),
                  ),
                )
              ],
            ),
          ),

          # ================= TABLE TITLE =================

          const Padding(

            padding: EdgeInsets.symmetric(
              horizontal: 16,
            ),

            child: Align(

              alignment: Alignment.centerLeft,

              child: Text(

                "LIVE TABLES",

                style: TextStyle(

                  color: Colors.amber,

                  fontSize: 22,

                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),

          const SizedBox(height: 10),

          # ================= TABLE LIST =================

          Expanded(

            child: ListView.builder(

              itemCount: tables.length,

              itemBuilder: (context, index) {

                final table = tables[index];

                return Container(

                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),

                  padding: const EdgeInsets.all(16),

                  decoration: BoxDecoration(

                    color: const Color(0xFF1A1A1A),

                    borderRadius:
                        BorderRadius.circular(25),

                    border: Border.all(
                      color: Colors.amber.shade700,
                      width: 1,
                    ),
                  ),

                  child: Column(

                    children: [

                      Row(

                        children: [

                          Container(

                            padding:
                                const EdgeInsets.all(12),

                            decoration: BoxDecoration(

                              color: Colors.amber
                                  .shade700,

                              borderRadius:
                                  BorderRadius.circular(
                                      18),
                            ),

                            child: const Icon(

                              Icons.casino,

                              color: Colors.black,

                              size: 30,
                            ),
                          ),

                          const SizedBox(width: 15),

                          Expanded(

                            child: Column(

                              crossAxisAlignment:
                                  CrossAxisAlignment
                                      .start,

                              children: [

                                Text(

                                  table.tableName,

                                  style: const TextStyle(

                                    color: Colors.white,

                                    fontSize: 20,

                                    fontWeight:
                                        FontWeight.bold,
                                  ),
                                ),

                                const SizedBox(
                                    height: 6),

                                Text(

                                  "Boot ₹${table.bootAmount}",

                                  style: TextStyle(

                                    color: Colors.amber
                                        .shade400,

                                    fontSize: 15,
                                  ),
                                ),
                              ],
                            ),
                          ),

                          Column(

                            children: [

                              const Icon(

                                Icons.people,

                                color: Colors.white70,
                              ),

                              const SizedBox(height: 5),

                              Text(

                                "${table.players}/${table.maxPlayers}",

                                style: const TextStyle(
                                  color: Colors.white,
                                ),
                              ),
                            ],
                          )
                        ],
                      ),

                      const SizedBox(height: 20),

                      Row(

                        children: [

                          Expanded(

                            child: ElevatedButton(

                              style:
                                  ElevatedButton.styleFrom(

                                backgroundColor:
                                    Colors.amber
                                        .shade700,

                                padding:
                                    const EdgeInsets
                                        .symmetric(
                                  vertical: 14,
                                ),

                                shape:
                                    RoundedRectangleBorder(

                                  borderRadius:
                                      BorderRadius
                                          .circular(18),
                                ),
                              ),

                              onPressed: () {

                                # ================= JOIN =================

                              },

                              child: const Text(

                                "JOIN TABLE",

                                style: TextStyle(

                                  color: Colors.black,

                                  fontWeight:
                                      FontWeight.bold,

                                  fontSize: 16,
                                ),
                              ),
                            ),
                          ),
                        ],
                      )
                    ],
                  ),
                );
              },
            ),
          )
        ],
      ),

      # ================= BOTTOM NAV =================

      bottomNavigationBar: BottomNavigationBar(

        backgroundColor: Colors.black,

        selectedItemColor: Colors.amber,

        unselectedItemColor: Colors.white60,

        currentIndex: 0,

        items: const [

          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: "Home",
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.casino),
            label: "Tables",
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.mic),
            label: "Voice",
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.person),
            label: "Profile",
          ),
        ],
      ),
    );
  }
}

# ================= TABLE MODEL =================

class TableModel {

  final String tableName;

  final int bootAmount;

  final int players;

  final int maxPlayers;

  TableModel({

    required this.tableName,

    required this.bootAmount,

    required this.players,

    required this.maxPlayers,
  });
}