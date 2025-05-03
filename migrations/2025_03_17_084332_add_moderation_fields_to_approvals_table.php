<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::table('approvals', function (Blueprint $table) {
            $table->enum('violation_level', ['none', 'low', 'medium', 'high'])
                ->nullable()
                ->default('none')
                ->after('remarks')
                ->comment('Mức độ vi phạm từ kiểm duyệt nội dung');

            $table->text('violations')
                ->nullable()
                ->after('violation_level')
                ->comment('Danh sách các vi phạm được phát hiện (JSON)');

            $table->json('violation_details')
                ->nullable()
                ->after('violations')
                ->comment('Chi tiết về các vi phạm và lý do (JSON)');
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('approvals', function (Blueprint $table) {
            $table->dropColumn('violation_level');
            $table->dropColumn('violations');
            $table->dropColumn('violation_details');
        });
    }
};
