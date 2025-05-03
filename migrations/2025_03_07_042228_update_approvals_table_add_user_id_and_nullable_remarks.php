<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up()
    {
        if (! Schema::hasColumn('approvals', 'user_id')) {
            Schema::table('approvals', function (Blueprint $table) {
                $table->foreignId('user_id')
                    ->nullable()
                    ->constrained('users', 'user_id')
                    ->after('article_id');
            });
        }

        Schema::table('approvals', function (Blueprint $table) {
            $table->text('remarks')->nullable()->change();
            $table->enum('type', ['article', 'role_upgrade'])
                ->default('article')
                ->change();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::table('approvals', function (Blueprint $table) {
            $table->dropColumn('user_id');
            $table->text('remarks')->nullable(false)->change();
        });
    }
};
